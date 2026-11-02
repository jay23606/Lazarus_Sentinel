import {useEffect, useRef} from 'react';
import cytoscape from 'cytoscape';
import type {Demo, Item} from './validation';
import {projectGraph} from './graph-view';

type Props={demo:Demo;selected:Item|undefined;mode:'path'|'overview';focusedEndpointId:string;selectedNodeId:string;onSelectNode:(id:string)=>void};
export default function Network({demo,selected,mode,focusedEndpointId,selectedNodeId,onSelectNode}:Props) {
  const ref=useRef<HTMLDivElement>(null), cy=useRef<cytoscape.Core|null>(null);
  const select=useRef(onSelectNode);select.current=onSelectNode;
  useEffect(()=>{
    if(!ref.current)return;
    const container=ref.current;
    const view=projectGraph(demo.graph,selected,mode,focusedEndpointId,container.clientWidth<=620);
    const pathNodes=new Set<string>(selected?.path_node_ids??[]), pathEdges=new Set<string>(selected?.path_edge_ids??[]);
    const c=cytoscape({container,elements:[...view.nodes.map(n=>({data:{id:n.id,label:`${n.type}\n${n.name}`,type:n.type},position:view.positions[n.id],classes:pathNodes.has(n.id)?'path':''})),...view.edges.map(e=>({data:{id:e.id,source:e.source,target:e.target,type:e.type,label:e.type},classes:pathEdges.has(e.id)?'path':''}))],layout:{name:'preset',fit:true,padding:35},minZoom:0.25,maxZoom:2.5,style:[
      {selector:'node',style:{label:'data(label)','font-size':14,'text-wrap':'wrap','text-max-width':'160px','text-valign':'center','text-halign':'center','background-color':'#e4edf8',color:'#142b45',shape:'round-rectangle',width:180,height:65,'border-width':1,'border-color':'#94acc5'}},
      {selector:'node[type = "API_ENDPOINT"]',style:{shape:'round-tag','background-color':'#dbeafe','border-color':'#2563eb'}},
      {selector:'node[type = "MODULE"]',style:{shape:'rectangle','background-color':'#eef0f3','border-style':'dashed'}},
      {selector:'node.path',style:{'border-width':3,'border-color':'#2464b7','background-color':'#dbeafe'}},
      {selector:'node.inspected',style:{'border-width':4,'border-color':'#b66d12','background-color':'#fff0d6'}},
      {selector:'edge',style:{label:'data(label)',width:1.5,'font-size':12,color:'#445b72','text-background-color':'#fff','text-background-opacity':0.95,'text-background-padding':'3px','line-color':'#91a5ba','target-arrow-color':'#91a5ba','target-arrow-shape':'triangle','curve-style':'bezier','control-point-step-size':38}},
      {selector:'edge[type = "CALLS"], edge[type = "HANDLES"]',style:{'line-color':'#8194aa','target-arrow-color':'#8194aa',width:2}},
      {selector:'edge.path',style:{'line-color':'#175cd3','target-arrow-color':'#175cd3',width:4,color:'#144a91','z-index':2}},
      {selector:'edge[type = "DEPENDS_ON"]',style:{'line-style':'dashed','line-color':'#a56a19','target-arrow-color':'#a56a19',label:'DEPENDS_ON\n(syntactic)'}},
      {selector:'edge[type = "IMPORTS"], edge[type = "CONTAINS"]',style:{'line-style':'dotted','font-size':11}}
    ]});
    cy.current=c;
    c.on('tap','node',event=>select.current(event.target.id()));
    let vertical=container.clientWidth<=620;
    const observer=typeof ResizeObserver==='undefined'?undefined:new ResizeObserver(()=>{
      c.resize(); const next=container.clientWidth<=620;
      if(mode==='path'&&next!==vertical){vertical=next;const p=projectGraph(demo.graph,selected,mode,focusedEndpointId,vertical).positions;c.nodes().forEach(n=>{n.position(p[n.id()]);});}
      c.fit(undefined,35);
    });observer?.observe(container);
    return ()=>{observer?.disconnect();c.destroy();cy.current=null;};
  },[demo,selected,mode,focusedEndpointId]);
  useEffect(()=>{const c=cy.current;if(!c)return;c.nodes().removeClass('inspected');c.getElementById(selectedNodeId).addClass('inspected');},[selectedNodeId,demo,selected,mode,focusedEndpointId]);
  const zoom=(factor:number)=>{const c=cy.current;if(c)c.zoom({level:Math.min(c.maxZoom(),Math.max(c.minZoom(),c.zoom()*factor)),renderedPosition:{x:c.width()/2,y:c.height()/2}});};
  const reset=()=>{const c=cy.current;if(!c||!ref.current)return;const p=projectGraph(demo.graph,selected,mode,focusedEndpointId,ref.current.clientWidth<=620).positions;c.nodes().forEach(n=>{n.position(p[n.id()]);});c.fit(undefined,35);};
  return <div className={`network-shell network-shell--${mode}`}><div className="graph-toolbar" role="group" aria-label="Graph viewport"><button onClick={()=>cy.current?.fit(undefined,35)}>Fit</button><button aria-label="Zoom in" onClick={()=>zoom(1.25)}>+</button><button aria-label="Zoom out" onClick={()=>zoom(0.8)}>−</button><button onClick={reset}>Reset</button></div><div className="network" ref={ref} role="img" aria-label={mode==='path'?'Focused structural context. Select a node to inspect; keyboard node controls follow below.':'Full stored structural graph. Keyboard node controls and exact identities follow below.'}/><ul className="graph-legend" aria-label="Graph legend"><li>Tag: API_ENDPOINT</li><li>Rounded card: FUNCTION</li><li>Dashed card: MODULE</li><li>Solid arrow: HANDLES / CALLS</li>{mode==='overview'&&<><li>Dashed arrow: DEPENDS_ON · syntactic, effectiveness unverified</li><li>Dotted arrow: IMPORTS / CONTAINS</li></>}{selected&&<li>Blue border / thick blue arrow: selected candidate path</li>}<li>Amber border: inspected node</li></ul></div>;
}
