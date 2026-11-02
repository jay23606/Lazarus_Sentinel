# 01 — Product and Engineering Requirements

Current implementation is governed by the [approved first-slice contract](13_FIRST_SLICE_CONTRACT.md). [Verified results](14_IMPLEMENTATION_REVIEW.md) describe the measured fixture run; [ordered next steps](15_NEXT_STEPS.md) are proposals for subsequent work, not approval to implement them.

## Implemented acceptance baseline

| Area | Delivered behavior |
|---|---|
| Intake | Only `fixture:fastapi-demo`; bounded explicit manifest, no arbitrary local path/upload |
| Identity | Exact source-byte snapshot and content revision including policy; no Git repository initialized |
| Structure | Modules/classes/functions/imports and unambiguous direct local calls |
| FastAPI | Supported literal routes, one-level router inclusion and explicit dependency declarations |
| Security | LS-AUTH-001 policy-defined authorization declaration-context assessment only |
| Evidence | Stable IDs, relative source ranges, byte hashes, analyzer/query identity and policy provenance |
| Unknowns | Unsupported/ambiguous control scopes produce diagnostics, never absence claims |
| Output | CLI JSON summary, graph/findings/coverage JSON, escaped hash-only Markdown report |
| Storage | SQLite scans, findings and committed artifact references |
| Runtime | Linear Python pipeline; no target execution, external model calls, HTTP API or UI |

Supported and unsupported syntax is enumerated in the first-slice contract. Matching declarations suppress a candidate without proving enforcement. Missing recognized declarations can produce LOW-confidence POTENTIAL_GAP candidates only for supported paths/control scopes and operator-defined protected operations. No policy means no sensitivity guess.

## Quality and safety requirements in force

Reproduce identical graph JSON for the same snapshot; preserve exact revision/evidence correspondence; reject invalid intake and stale source; publish only validated references; expose partial coverage. Keep source excerpts out of persisted reports and sanitize public diagnostic text. Resource-bounded child parsing is not an OS security sandbox.

The 2026-11-02 baseline recorded 73 passing tests plus clean Ruff and strict mypy. This is fixture engineering verification, not a broad performance or security certification.

## Future requirements — not implemented or an approved expansion

Broader authorized intake needs a separately reviewed authorization/isolation contract. Future inventory, additional language adapters, data-flow/trust rules, identity/asset enrichment, multi-adapter integration and incremental scans require explicit supported subsets and tests. Archive support needs extraction/path/expanded-size defenses before use.

Future API/UI requirements include findings/path navigation, coverage diagnostics, accessible graph alternatives and review rationale. Runtime LLM explanation requires verified provider access, minimized/redacted context, output/evidence-reference validation and disclosed egress. LangGraph is optional if measured state/concurrency needs justify it. Generalized latency, memory and accuracy targets have not been measured or accepted.
