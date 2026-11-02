# 07 — Reporting Experience and Frontend Roadmap

> Team/platform update (2026-11-02): [team handoff](21_TEAM_HANDOFF.md), [finite next-phase plan](22_NEXT_PHASE_PLAN.md), and [current portability/publication evidence](23_PORTABILITY_AND_RELEASE_VERIFICATION.md) supersede earlier onboarding, remote-state and platform assumptions. Historical checks below retain their original date and scope.


## Integrated demo status — 2026-11-02

The approved [demo contract](16_DEMO_DELIVERY_CONTRACT.md) is implemented alongside the preserved first-slice analyzer: immutable hash-verified bundles, disabled/mock explanations with a gated Meta adapter, and a fixed React/Vite/TypeScript/Cytoscape viewer. See [capability gates](17_CAPABILITY_AND_RESEARCH_REPORT.md), [finite evaluation](18_DEMO_EVALUATION.md), and [integrated verification](19_INTEGRATED_DEMO_REVIEW.md) for current checks and review disposition. Document 14 remains historical first-slice evidence; its 73-test count is not the integrated total.

Baseline commit `7797b85`, integrated demo `4f0346c` and viewer refinement `2cda191` are preserved on `feat/integrated-demo`. Publication to the owner-specified repository is now authorized; actual remote/CI outcomes are recorded in document 23. License and submission decisions remain unresolved. Only fixed synthetic intake is supported. Live access is BLOCKED by the missing key; zero paid calls were made. Joern setup is blocked and analysis NOT_ATTEMPTED; data/trust rules remain NOT_IMPLEMENTED. OS sandbox launch failed before execution, so broader intake remains blocked.

## Viewer clarity increment — 2026-11-02

[Document20](20_VIEWER_CLARITY_AND_DESIGN.md) records the delivered guided investigation experience: endpoint search, exact focused paths, deterministic full graph, node/edge labels, graph controls, node-specific evidence, responsive layout and keyboard alternatives. Current checks are115backend/16frontend tests, with independent Astra semantics review. Document19 preserves the earlier integrated delivery measurements.

## Current user experience

A fixed React/Vite/TypeScript/Cytoscape viewer loads only the reviewed synthetic bundle from `frontend/public/demo/v1/`. It provides graph, finding/path/evidence tables, endpoint declarations, coverage and recorded mock explanation provenance. There is no HTTP API, upload, scan-start form or arbitrary URL/path loader. The CLI and Markdown reports remain usable. The [verified implementation review](14_IMPLEMENTATION_REVIEW.md) links the latest report and measurements.

The report presents source revision, coverage/diagnostics, endpoint labels, ordered structural paths and declared dependencies. Evidence retains relative locations/hashes rather than source excerpts. Candidates remain CANDIDATE / NEEDS_REVIEW / POTENTIAL_GAP with LOW confidence; matching dependency declarations explicitly have effectiveness unverified. Human review occurs outside an application triage workflow.

Current demonstration: run the fixture scan, explain expected exit 2/PARTIAL, inspect GET /weak and GET /authenticated candidates, compare recognized declarations and the unflagged public/no-policy path, then show unsupported dynamic registration. Repeat graph equality and artifact hashes support reproducibility; no data-flow or runtime-security claim follows.

## Delivered frontend and remaining work

Dependencies are project-local and locked in `frontend/package-lock.json`. Run `npm ci --prefix frontend`, then `npm run dev --prefix frontend`; the dev server binds to loopback. `npm run typecheck --prefix frontend`, `npm run lint --prefix frontend`, `npm test --prefix frontend`, and `npm run build --prefix frontend` verify the trusted viewer. Current final outcomes and browser limitations are recorded in document 19.

Delivered presentation scope (persistent triage remains future work):

- Scan overview: revision, status, timing, graph counts, findings and explicit coverage gaps.
- Application graph: evidence-backed nodes/edges, search/filter, local neighborhoods and selected candidate path.
- Findings/detail: separate severity/confidence/verification, observation versus hypothesis, source ranges/hashes, assumptions, unknowns and review actions.
- Coverage/diagnostics: supported, partial, failed, skipped and unsupported scope with reasons.

A future triage UI depends on a new persistence/auth contract. Source excerpt display depends on a separately defined retention/access policy. Do not portray these features as present.

## UX acceptance and limits

The graph should support investigation, with a table/report alternative, keyboard access and status labels beyond color. Cap initial elements, expand neighborhoods and avoid expensive repeated layouts. Explain every relationship through evidence and keep uncertainty visible.

Use “candidate,” “no matching declaration was recognized,” and “partially analyzed.” Avoid “confirmed vulnerability,” “no authorization exists,” “secure comparison path,” or qualitative confidence presented as a calibrated probability. Demonstrations should use reproducible fixture output, not fabricated findings or a required live model response.

Cytoscape.js reference for future evaluation: https://js.cytoscape.org/
