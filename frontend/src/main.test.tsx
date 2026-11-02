// @vitest-environment jsdom
import React from 'react';
import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen, within} from '@testing-library/react';
import graph from './testdata/graph.json';
import {App} from './main';
import {loadDemo, type Demo} from './validation';

vi.mock('./validation',()=>({loadDemo:vi.fn()}));
vi.mock('cytoscape',()=>({default:()=>({destroy:vi.fn(),elements:()=>({removeClass:vi.fn()}),getElementById:()=>({addClass:vi.fn()})})}));
afterEach(()=>{cleanup();vi.clearAllMocks();});

it('selection renders exact ordered node and edge IDs and escapes hostile labels',async()=>{
  const data=structuredClone(graph);
  const selected=data.findings[1];
  const hostile='<img src=x onerror=alert(1)>';
  data.nodes.find(n=>n.id===selected.entry_node_id)!.name=hostile;
  vi.mocked(loadDemo).mockResolvedValue({manifest:{scan:{status:'PARTIAL',profile:'reduced-static-auth',revision:data.repository.revision}},graph:data,annotations:[]} as unknown as Demo);
  const view=render(<App/>);
  const button=await screen.findByRole('button',{name:new RegExp('img src=x')});
  fireEvent.click(button);
  expect(button.getAttribute('aria-pressed')).toBe('true');
  const table=screen.getByRole('heading',{name:'Ordered evidence path'}).parentElement!.querySelector('table')!;
  const rows=within(table).getAllByRole('row').slice(1);
  expect(rows).toHaveLength(selected.path_node_ids.length);
  rows.forEach((row,i)=>{
    expect(row.textContent).toContain(selected.path_node_ids[i]);
    if(selected.path_edge_ids[i]) expect(row.textContent).toContain(selected.path_edge_ids[i]);
  });
  expect(view.container.querySelector('img')).toBeNull();
  expect(view.container.textContent).toContain(hostile);
});

it('invalid bundle suppresses graph and counts with a display failure',async()=>{
  vi.mocked(loadDemo).mockRejectedValue(new Error('bad hash'));
  render(<App/>);
  expect((await screen.findByRole('alert')).textContent).toContain('Display verification failed');
  expect(screen.queryByText('candidate findings')).toBeNull();
  expect(screen.queryByRole('img')).toBeNull();
  expect(screen.queryByRole('button')).toBeNull();
});
