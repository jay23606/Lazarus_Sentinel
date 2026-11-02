// @vitest-environment jsdom
import {cleanup, fireEvent, render, screen} from '@testing-library/react';
import {afterEach, expect, it, vi} from 'vitest';
import cytoscape from 'cytoscape';
import Network from './Network';
import graph from './testdata/graph.json';
import type {Demo} from './validation';

const mocks=vi.hoisted(()=>({fit:vi.fn(),zoom:vi.fn(()=>1),destroy:vi.fn(),on:vi.fn(),removeClass:vi.fn(),addClass:vi.fn()}));
vi.mock('cytoscape',()=>({default:vi.fn(()=>({...mocks,nodes:()=>({removeClass:mocks.removeClass,forEach:vi.fn()}),getElementById:()=>({addClass:mocks.addClass}),maxZoom:()=>2.5,minZoom:()=>0.25,width:()=>600,height:()=>500}))}));
afterEach(()=>{cleanup();vi.clearAllMocks();});
it('renders exact stored path labels, exposes viewport controls and selects real node identities',()=>{
  const f=graph.findings[0], select=vi.fn();
  render(<Network demo={{graph} as unknown as Demo} selected={f} mode="path" focusedEndpointId={f.entry_node_id} selectedNodeId={f.entry_node_id} onSelectNode={select}/>);
  const options=vi.mocked(cytoscape).mock.calls[0][0] as unknown as cytoscape.CytoscapeOptions;
  const elements=options.elements as cytoscape.ElementDefinition[];
  expect(elements.map(e=>e.data.id)).toEqual([...f.path_node_ids,...f.path_edge_ids]);
  expect(elements[0].data.label).toBe(`API_ENDPOINT\n${graph.nodes.find(n=>n.id===f.entry_node_id)!.name}`);
  fireEvent.click(screen.getByRole('button',{name:'Fit'}));
  expect(mocks.fit).toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button',{name:'Zoom in'}));
  expect(mocks.zoom).toHaveBeenCalledWith(expect.objectContaining({level:1.25}));
  const callback=mocks.on.mock.calls[0][2];
  callback({target:{id:()=>f.entry_node_id}});
  expect(select).toHaveBeenCalledWith(f.entry_node_id);
  expect(screen.getByLabelText('Graph legend').textContent).toContain('FUNCTION');
  expect(screen.getByLabelText('Graph legend').parentElement?.className).toContain('network-shell--path');
});
it('overview highlights only the exact stored candidate nodes and edges',()=>{
  const f=graph.findings[0];
  const view=render(<Network demo={{graph} as unknown as Demo} selected={f} mode="overview" focusedEndpointId={f.entry_node_id} selectedNodeId="" onSelectNode={vi.fn()}/>);
  const options=vi.mocked(cytoscape).mock.calls[0][0] as unknown as cytoscape.CytoscapeOptions;
  const elements=options.elements as cytoscape.ElementDefinition[];
  expect(screen.getByLabelText('Graph legend').parentElement?.className).toContain('network-shell--overview');
  expect(elements.filter(e=>e.classes==='path').map(e=>e.data.id)).toEqual(expect.arrayContaining([...f.path_node_ids,...f.path_edge_ids]));
  expect(elements.filter(e=>e.classes==='path')).toHaveLength(f.path_node_ids.length+f.path_edge_ids.length);
  expect(options.wheelSensitivity).toBeUndefined();
  view.unmount();
  render(<Network demo={{graph} as unknown as Demo} selected={undefined} mode="overview" focusedEndpointId={f.entry_node_id} selectedNodeId="" onSelectNode={vi.fn()}/>);
  const noCandidate=vi.mocked(cytoscape).mock.calls[1][0] as unknown as cytoscape.CytoscapeOptions;
  expect((noCandidate.elements as cytoscape.ElementDefinition[]).some(e=>e.classes==='path')).toBe(false);
});
