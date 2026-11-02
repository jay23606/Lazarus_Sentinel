import { describe, it, expect } from 'vitest';
import { validateGraph, type Graph } from './validation';

describe('graph semantics', () => {
  it('rejects duplicate identities and dangling edges', () => {
    const g = {repository:{revision:'r'},nodes:[{id:'n',evidence_ids:[]},{id:'n',evidence_ids:[]}],edges:[],evidence:[],findings:[],coverage:[],diagnostics:[]};
    expect(() => validateGraph(g, 'r')).toThrow();
    g.nodes.pop();
    g.edges.push({id:'e', source:'n',target:'missing',evidence_ids:[]} as never);
    expect(() => validateGraph(g, 'r')).toThrow();
  });
});

import { vi, afterEach } from 'vitest';
import { webcrypto } from 'node:crypto';
import graph from './testdata/graph.json';
import { loadDemo } from './validation';

const encoder = new TextEncoder();
const bytes = encoder.encode(JSON.stringify(graph));
const hex = (data:ArrayBuffer) => Array.from(new Uint8Array(data)).map(x=>x.toString(16).padStart(2,'0')).join('');
afterEach(()=>vi.unstubAllGlobals());
it('verifies exact graph bytes before exposing results', async()=>{
  vi.stubGlobal('crypto',webcrypto);
  const hash=hex(await webcrypto.subtle.digest('SHA-256',bytes));
  const manifest={bundle_version:'0.1.0',bundle_id:'11111111-1111-4111-8111-111111111111',origin:'controlled-synthetic-fixture',generator_version:'0.1.0',scan:{scan_id:'11111111-1111-4111-8111-111111111111',revision:graph.repository.revision,status:'PARTIAL',profile:'reduced-static-auth'},artifacts:{'graph.json':{sha256:hash,size:bytes.length}}};
  let changed=false;
  vi.stubGlobal('fetch',async (url:string)=>new Response(url.endsWith('bundle.json')?JSON.stringify(manifest):changed?new Uint8Array([...bytes.slice(0,-1),32]):bytes));
  expect((await loadDemo()).graph.findings).toHaveLength(2);
  changed=true;
  await expect(loadDemo()).rejects.toThrow('Integrity check failed');
});

import annotation from './testdata/annotation.json';
it('checks recorded annotation request and citation bindings',async()=>{
  vi.stubGlobal('crypto',webcrypto);
  const hash=hex(await webcrypto.subtle.digest('SHA-256',bytes));
  const sidecar={annotation_version:'0.1.0',annotations:[{...annotation,graph_sha256:hash}]};
  let sideBytes=encoder.encode(JSON.stringify(sidecar));
  const manifest={bundle_version:'0.1.0',bundle_id:'11111111-1111-4111-8111-111111111111',origin:'controlled-synthetic-fixture',generator_version:'0.1.0',scan:{scan_id:'11111111-1111-4111-8111-111111111111',revision:graph.repository.revision,status:'PARTIAL',profile:'reduced-static-auth'},artifacts:{'graph.json':{sha256:hash,size:bytes.length},'explanations.json':{sha256:'',size:0}}};
  const seal=async()=>{sideBytes=encoder.encode(JSON.stringify(sidecar));manifest.artifacts['explanations.json']={sha256:hex(await webcrypto.subtle.digest('SHA-256',sideBytes)),size:sideBytes.length};};
  vi.stubGlobal('fetch',async (url:string)=>new Response(url.endsWith('bundle.json')?JSON.stringify(manifest):url.endsWith('graph.json')?bytes:sideBytes));
  await seal(); expect((await loadDemo()).annotations).toHaveLength(1);
  sidecar.annotations[0].request_sha256='0'.repeat(64); await seal();
  await expect(loadDemo()).rejects.toThrow('request binding');
  sidecar.annotations[0].request_sha256=annotation.request_sha256; sidecar.annotations[0].response.evidence_ids=['not-an-evidence-id']; await seal();
  await expect(loadDemo()).rejects.toThrow('explanation binding');
});
it('rejects incomplete path evidence and wrong edge semantics',()=>{
  const copy=structuredClone(graph);
  copy.findings[0].evidence_ids=[];
  expect(()=>validateGraph(copy as unknown as Graph,copy.repository.revision)).toThrow();
  const changed=structuredClone(graph);
  changed.edges.find(e=>e.id===changed.findings[0].path_edge_ids[0])!.type='CALLS';
  expect(()=>validateGraph(changed as unknown as Graph,changed.repository.revision)).toThrow('ordered finding path');
});
it('rejects node/edge identity collisions before graph rendering',()=>{
  const changed=structuredClone(graph);
  const edge=changed.edges.find(e=>!changed.findings.some(f=>f.path_edge_ids.includes(e.id)))!;
  edge.id=changed.nodes[0].id;
  expect(()=>validateGraph(changed as unknown as Graph,changed.repository.revision)).toThrow('element identity');
});
it('rejects a completed manifest for partial graph coverage',async()=>{
  vi.stubGlobal('crypto',webcrypto);
  const hash=hex(await webcrypto.subtle.digest('SHA-256',bytes));
  const manifest={bundle_version:'0.1.0',bundle_id:'11111111-1111-4111-8111-111111111111',origin:'controlled-synthetic-fixture',generator_version:'0.1.0',scan:{scan_id:'11111111-1111-4111-8111-111111111111',revision:graph.repository.revision,status:'COMPLETED',profile:'reduced-static-auth'},artifacts:{'graph.json':{sha256:hash,size:bytes.length}}};
  vi.stubGlobal('fetch',async(url:string)=>new Response(url.endsWith('bundle.json')?JSON.stringify(manifest):bytes));
  await expect(loadDemo()).rejects.toThrow('coverage status');
});
