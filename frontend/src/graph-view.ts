import type {Graph, Item} from './validation';

export function projectGraph(graph:Pick<Graph,'nodes'|'edges'>, selected:Item|undefined, mode:'path'|'overview', endpointId:string, vertical=false) {
  let nodes:Item[], edges:Item[];
  const depth=new Map<string,number>();
  if(mode==='overview') {
    nodes=[...graph.nodes].sort((a,b)=>a.name.localeCompare(b.name)||a.id.localeCompare(b.id));
    edges=[...graph.edges];
  } else if(selected) {
    nodes=selected.path_node_ids.map((id:string)=>graph.nodes.find(n=>n.id===id)!);
    edges=selected.path_edge_ids.map((id:string)=>graph.edges.find(e=>e.id===id)!);
    nodes.forEach((n,i)=>depth.set(n.id,i));
  } else {
    const ids=new Set(graph.nodes.some(n=>n.id===endpointId)?[endpointId]:[]);
    depth.set(endpointId,0); edges=[];
    // Follow stored structure only; declaration edges are not execution paths.
    for(const id of ids) for(const e of graph.edges) if(e.source===id && ['HANDLES','CALLS'].includes(e.type)) {
      edges.push(e);
      if(!ids.has(e.target)) {ids.add(e.target);depth.set(e.target,(depth.get(id)??0)+1);}
    }
    nodes=[...ids].map(id=>graph.nodes.find(n=>n.id===id)!);
  }
  const positions:Record<string,{x:number;y:number}>={};
  const rows=new Map<number,number>();
  for(const n of nodes) {
    const column=mode==='path' ? depth.get(n.id)??0 : n.type==='MODULE'?0:n.type==='API_ENDPOINT'?1:graph.edges.some(e=>e.type==='HANDLES'&&e.target===n.id)?2:3;
    const row=rows.get(column)??0;rows.set(column,row+1);
    positions[n.id]=mode==='path'&&vertical ? {x:120+row*210,y:70+column*145} : {x:110+column*235,y:65+row*100};
  }
  return {nodes,edges,positions};
}
