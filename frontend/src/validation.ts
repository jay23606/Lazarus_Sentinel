import Ajv2020 from 'ajv/dist/2020';
import bundleSchema from './schemas/bundle.schema.json';
import graphSchema from './schemas/graph.schema.json';
import explanationSchema from './schemas/explanations.schema.json';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type Item = { id:string; [key:string]: any }; // Graph properties are analyzer-defined.
export type Graph = { repository:{revision:string}; nodes:Item[]; edges:Item[]; evidence:Item[]; findings:Item[]; coverage:Item[]; diagnostics:Item[] };
export type Manifest = { scan:{scan_id:string; revision:string; status:string; profile:string}; artifacts:Record<string,{size:number; sha256:string}> };
export type Demo = {manifest:Manifest; graph:Graph; annotations:Item[]};
const ajv = new Ajv2020({strict:false});
const bundleCheck = ajv.compile(bundleSchema), graphCheck = ajv.compile(graphSchema), explanationCheck = ajv.compile(explanationSchema);
const fail = (message:string):never => { throw new Error(message); };
const unique = (items:Item[], name:string) => {
  const ids = new Set(items.map(x => x.id));
  if (ids.size !== items.length || items.some(x => !x.id)) fail(`Duplicate or missing ${name} identity`);
  return ids;
};
const references = (ids:string[], valid:Set<string>) => ids.every(id => valid.has(id));
export function validateGraph(graph:Graph, revision:string) {
  if (graph.repository.revision !== revision || !graph.nodes.length || graph.nodes.length > 500 || graph.edges.length > 2000) fail('Graph revision or size is invalid');
  const nodes = unique(graph.nodes,'node'), edges = unique(graph.edges,'edge'), evidence = unique(graph.evidence,'evidence');
  unique(graph.findings,'finding');
  if(graph.edges.some(e=>nodes.has(e.id))) fail('Duplicate graph element identity');
  for (const e of graph.evidence) if (e.repository_revision !== revision || e.end_line < e.start_line || !e.file_path || e.file_path.startsWith('/') || e.file_path.split('/').includes('..') || e.file_path.includes('\\') || !/^sha256:[0-9a-f]{64}$/.test(e.excerpt_hash)) fail('Invalid evidence');
  for (const x of [...graph.nodes,...graph.edges]) if (!references(x.evidence_ids, evidence) || !x.evidence_ids.length) fail('Missing evidence reference');
  for (const e of graph.edges) if (!nodes.has(e.source) || !nodes.has(e.target)) fail('Dangling edge');
  for (const n of graph.nodes.filter(x=>x.type==='API_ENDPOINT')) if (!Array.isArray(n.properties.dependencies) || !n.properties.dependencies.every((d:unknown)=>typeof d==='string') || typeof n.properties.control_scope_supported!=='boolean') fail('Unknown endpoint metadata');
  for (const f of graph.findings) {
    if (f.repository_revision !== revision || !f.evidence_ids.length || !references(f.evidence_ids,evidence) || !references(f.path_node_ids,nodes) || !references(f.path_edge_ids,edges) || f.path_node_ids[0] !== f.entry_node_id || f.path_node_ids.length !== f.path_edge_ids.length + 1) fail('Invalid finding references');
    const required=[...f.path_node_ids.flatMap((id:string)=>graph.nodes.find(n=>n.id===id)!.evidence_ids),...f.path_edge_ids.flatMap((id:string)=>graph.edges.find(e=>e.id===id)!.evidence_ids)];
    if(!references(required,new Set(f.evidence_ids))) fail('Incomplete finding evidence');
    f.path_edge_ids.forEach((id:string, i:number) => { const e=graph.edges.find(x => x.id===id)!; if(e.source!==f.path_node_ids[i] || e.target!==f.path_node_ids[i+1] || e.type!==(i===0?'HANDLES':'CALLS') || e.fact_status!=='OBSERVED') fail('Invalid ordered finding path'); });
  }
}
async function readBounded(name:string, limit:number) {
  const response = await fetch(`/demo/v1/${name}`, {cache:'no-store'});
  if (!response.ok || !response.body) fail(`Cannot load ${name}`);
  const reader = response.body!.getReader(); const parts:Uint8Array[]=[]; let size=0;
  while (true) { const {done,value}=await reader.read(); if(done) break; size+=value.length; if(size>limit) { await reader.cancel(); fail('Bundle exceeds size limit'); } parts.push(value); }
  const bytes=new Uint8Array(size); let offset=0; for(const part of parts){bytes.set(part,offset); offset+=part.length;} return bytes;
}
const parse = (bytes:Uint8Array) => JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
const sha = async (bytes:Uint8Array) => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes as BufferSource))).map(x=>x.toString(16).padStart(2,'0')).join('');
const uuid = (x:string) => /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(x);
export async function loadDemo():Promise<Demo> {
  const manifestBytes=await readBounded('bundle.json',1048576), raw=parse(manifestBytes);
  if (!bundleCheck(raw)) fail('Invalid bundle manifest');
  const manifest=raw as unknown as Manifest & {bundle_id:string};
  if (!uuid(manifest.bundle_id) || !uuid(manifest.scan.scan_id)) fail('Invalid bundle identity'); const names=Object.keys(manifest.artifacts).sort();
  if(names.join(',') !== 'graph.json' && names.join(',') !== 'explanations.json,graph.json') fail('Unexpected bundle artifacts');
  let size=manifestBytes.length; const payloads:Record<string,Uint8Array>={};
  for (const name of names) { const bytes=await readBounded(name,1048576-size); size+=bytes.length; const expected=manifest.artifacts[name]; if(bytes.length!==expected.size || await sha(bytes)!==expected.sha256) fail(`Integrity check failed for ${name}`); payloads[name]=bytes; }
  const graph=parse(payloads['graph.json']); if(!graphCheck(graph)) fail('Invalid graph schema'); validateGraph(graph,manifest.scan.revision);
  const partial=graph.coverage.some((c:Item)=>['PARTIALLY_ANALYZED','UNSUPPORTED_LANGUAGE','PARSER_ERROR','TIMEOUT'].includes(c.status));
  if(manifest.scan.status!==(partial?'PARTIAL':'COMPLETED')) fail('Invalid scan coverage status');
  let annotations:Item[]=[];
  if(payloads['explanations.json']) { const envelope=parse(payloads['explanations.json']); if(!explanationCheck(envelope)) fail('Invalid explanation schema'); annotations=envelope.annotations;
    for(const a of annotations) { if(!a.response.summary.trim() || !a.response.why_it_matters.trim() || a.response.limitations.some((x:string)=>!x.trim())) fail('Invalid explanation text'); const f=graph.findings.find((x:Item)=>x.id===a.finding_id); if(!uuid(a.annotation_id) || a.scan_id!==manifest.scan.scan_id || a.revision!==manifest.scan.revision || a.graph_sha256!==manifest.artifacts['graph.json'].sha256 || !f || !references(a.response.evidence_ids,new Set(f.evidence_ids)) || new Set(a.response.evidence_ids).size!==a.response.evidence_ids.length || ![['mock','deterministic-mock-v1','mock'],['meta','muse-spark-1.3','live']].some(x=>x.join('|')===[a.provider,a.model,a.generation].join('|')) || !Number.isFinite(Date.parse(a.created_at)) || !/(Z|[+-]\d\d:\d\d)$/.test(a.created_at)) fail('Invalid explanation binding'); }
  }
  for (const a of annotations) {
    const f=graph.findings.find((x:Item)=>x.id===a.finding_id)!;
    const pick=(x:Item, keys:string[])=>Object.fromEntries(keys.map(k=>[k,x[k]]));
    const context={finding_id:f.id,rule_id:f.rule_id,path_nodes:f.path_node_ids.map((id:string)=>pick(graph.nodes.find((n:Item)=>n.id===id)!,['id','name','type','qualified_name'])),path_edges:f.path_edge_ids.map((id:string)=>pick(graph.edges.find((e:Item)=>e.id===id)!,['id','source','target','type'])),evidence:graph.evidence.filter((e:Item)=>f.evidence_ids.includes(e.id)).sort((x:Item,y:Item)=>x.id.localeCompare(y.id)).map((e:Item)=>pick(e,['id','repository_revision','file_path','start_line','end_line','excerpt_hash'])),assumptions:f.assumptions,unknowns:f.unknowns};
    const canonical=(value:unknown):string=> { if(Array.isArray(value)) return '['+value.map(canonical).join(',')+']'; if(value && typeof value==='object') return '{'+Object.entries(value).sort(([a],[b])=>a<b?-1:a>b?1:0).map(([k,v])=>canonical(k)+':'+canonical(v)).join(',')+'}'; return JSON.stringify(value).replace(/[\u007f-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0')); };
    const request={context,prompt_version:'evidence-explanation-v1',provider:a.provider,model:a.model};
    if(await sha(new TextEncoder().encode(canonical(request)))!==a.request_sha256) fail('Invalid explanation request binding');
  }
  return {manifest,graph,annotations};
}
