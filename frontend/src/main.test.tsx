// @vitest-environment jsdom
import React from 'react';
import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen, within} from '@testing-library/react';
import graph from './testdata/graph.json';
import {App} from './main';
import {loadDemo, type Demo} from './validation';

vi.mock('./validation',()=>({loadDemo:vi.fn()}));
vi.mock('./Network',()=>({default:()=> <div data-testid="network"/>}));
afterEach(()=>{cleanup();vi.clearAllMocks();});
const demo = (data=graph) => ({manifest:{scan:{status:'PARTIAL',profile:'reduced-static-auth',revision:data.repository.revision}},graph:data,annotations:[{finding_id:data.findings[0].id,generation:'mock',provider:'mock',model:'deterministic-mock-v1',response:{summary:'Mock explanation',why_it_matters:'Fixture',limitations:[]}}]} as unknown as Demo);

it('guides selection and clears candidate details for an endpoint without a finding',async()=>{
  vi.mocked(loadDemo).mockResolvedValue(demo());
  render(<App/>);
  expect(await screen.findByText('Trace authorization questions back to code')).toBeTruthy();
  expect(screen.getByText('Mock explanation')).toBeTruthy();
  const endpoint=graph.nodes.find(n=>n.type==='API_ENDPOINT' && !graph.findings.some(f=>f.entry_node_id===n.id))!;
  fireEvent.change(screen.getByLabelText('Search endpoints'),{target:{value:endpoint.name}});
  fireEvent.click(screen.getByRole('button',{name:new RegExp(endpoint.name.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'))}));
  expect(screen.getAllByText('No candidate in this scan').length).toBeGreaterThan(0);
  expect(screen.queryByText('Mock explanation')).toBeNull();
  expect(screen.queryByText('Severity')).toBeNull();
  expect(screen.queryByRole('heading',{name:'Ordered evidence path'})).toBeNull();
});

it('selection renders exact ordered node and edge IDs and escapes hostile labels',async()=>{
  const data=structuredClone(graph); const selected=data.findings[1]; const hostile='<img src=x onerror=alert(1)>';
  data.nodes.find(n=>n.id===selected.entry_node_id)!.name=hostile;
  vi.mocked(loadDemo).mockResolvedValue(demo(data));
  const view=render(<App/>);
  fireEvent.click(await screen.findByRole('button',{name:new RegExp('img src=x')}));
  const table=screen.getByRole('heading',{name:'Ordered evidence path'}).parentElement!.querySelector('table')!;
  const rows=within(table).getAllByRole('row').slice(1);
  expect(rows).toHaveLength(selected.path_node_ids.length);
  rows.forEach((row,i)=>{expect(row.textContent).toContain(selected.path_node_ids[i]); if(selected.path_edge_ids[i]) expect(row.textContent).toContain(selected.path_edge_ids[i]);});
  expect(view.container.querySelector('img')).toBeNull();
});

it('invalid bundle suppresses graph and counts with a display failure',async()=>{
  vi.mocked(loadDemo).mockRejectedValue(new Error('bad hash')); render(<App/>);
  expect((await screen.findByRole('alert')).textContent).toContain('Display verification failed');
  expect(screen.queryByTestId('network')).toBeNull(); expect(screen.queryByRole('button')).toBeNull();
});
