# 01 — Product and Engineering Requirements

## Integrated demo status — 2026-11-02

The approved [demo contract](16_DEMO_DELIVERY_CONTRACT.md) is implemented alongside the preserved first-slice analyzer: immutable hash-verified bundles, disabled/mock explanations with a gated Meta adapter, and a fixed React/Vite/TypeScript/Cytoscape viewer. See [capability gates](17_CAPABILITY_AND_RESEARCH_REPORT.md), [finite evaluation](18_DEMO_EVALUATION.md), and [integrated verification](19_INTEGRATED_DEMO_REVIEW.md) for current checks and review disposition. Document 14 remains historical first-slice evidence; its 73-test count is not the integrated total.

Local baseline commit `7797b85` is preserved on `feat/integrated-demo`; no remote, publication, submission or license selection is implied. Only fixed synthetic intake is supported. Live access is BLOCKED by the missing key; zero paid calls were made. Joern setup is blocked and analysis NOT_ATTEMPTED; data/trust rules remain NOT_IMPLEMENTED. OS sandbox launch failed before execution, so broader intake remains blocked.

## Implemented acceptance baseline

| Area | Delivered behavior |
|---|---|
| Intake | Only `fixture:fastapi-demo`; bounded explicit manifest, no arbitrary local path/upload |
| Identity | Exact source-byte snapshot and content revision including policy; local baseline commit 7797b85; byte revision remains authoritative |
| Structure | Modules/classes/functions/imports and unambiguous direct local calls |
| FastAPI | Supported literal routes, one-level router inclusion and explicit dependency declarations |
| Security | LS-AUTH-001 policy-defined authorization declaration-context assessment only |
| Evidence | Stable IDs, relative source ranges, byte hashes, analyzer/query identity and policy provenance |
| Unknowns | Unsupported/ambiguous control scopes produce diagnostics, never absence claims |
| Output | CLI JSON summary, graph/findings/coverage JSON, escaped hash-only Markdown report |
| Storage | SQLite scans, findings and committed artifact references |
| Runtime | Linear Python pipeline; no target execution or HTTP API; optional explanations and fixed artifact UI are separate from scanning |

Supported and unsupported syntax is enumerated in the first-slice contract. Matching declarations suppress a candidate without proving enforcement. Missing recognized declarations can produce LOW-confidence POTENTIAL_GAP candidates only for supported paths/control scopes and operator-defined protected operations. No policy means no sensitivity guess.

## Quality and safety requirements in force

Reproduce identical graph JSON for the same snapshot; preserve exact revision/evidence correspondence; reject invalid intake and stale source; publish only validated references; expose partial coverage. Keep source excerpts out of persisted reports and sanitize public diagnostic text. Resource-bounded child parsing is not an OS security sandbox.

The 2026-11-02 baseline recorded 73 passing tests plus clean Ruff and strict mypy. This is fixture engineering verification, not a broad performance or security certification.

## Future requirements — not implemented or an approved expansion

Broader authorized intake needs a separately reviewed authorization/isolation contract. Future inventory, additional language adapters, data-flow/trust rules, identity/asset enrichment, multi-adapter integration and incremental scans require explicit supported subsets and tests. Archive support needs extraction/path/expanded-size defenses before use.

The fixed viewer delivers findings/path navigation, coverage diagnostics and accessible graph alternatives. Persisted review rationale and multi-user/API workflows remain future requirements. Runtime LLM explanation requires verified provider access, minimized/redacted context, output/evidence-reference validation and disclosed egress. LangGraph is optional if measured state/concurrency needs justify it. Generalized latency, memory and accuracy targets have not been measured or accepted.
