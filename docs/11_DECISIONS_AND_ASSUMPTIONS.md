# 11 — Decisions, assumptions and open gates

Updated 2026-11-02. Approved current scope is in [document 13](13_FIRST_SLICE_CONTRACT.md); verified behavior in [document 14](14_IMPLEMENTATION_REVIEW.md). [Document 15](15_NEXT_STEPS.md) contains recommendations, not newly accepted implementation decisions.

## Decision register — preserve identity and scope

| ID | Decision | Current interpretation |
|---|---|---|
| D-001 | Graph-first application-security product, not a generic chatbot | Product objective retained; evidence correlation is the value proposition |
| D-002 | Code, application and security-context layers | Target model; only emitted facts/policy context are claimed today |
| D-003 | Reuse analyzers rather than write a universal compiler | AST structure adapter now; no substitute taint compiler |
| D-004 | Joern candidate subject to Python/FastAPI measurement | NOT_ATTEMPTED, not rejected; optional next spike N09 |
| D-005 | AST fallback with honest limitations | Approved primary first-slice structure path; no CPG/data-flow claim |
| D-006 | NetworkX + SQLite + portable JSON | Implemented MultiDiGraph, scans/findings/artifact refs and JSON/Markdown |
| D-007 | React/Vite + Cytoscape.js frontend direction | Proposed next presentation stack, not installed/implemented |
| D-008 | LangGraph only when its state/concurrency adds value | Deferred; D-018 uses linear Python now |
| D-009 | Meta/Muse Spark intended hackathon runtime provider | Access, event suitability and privacy/request gates unverified; disabled today |
| D-010 | Model explains evidence rather than establishes facts | Safety invariant for later integration; no current provider |
| D-011 | Defensive static read-only product | No exploitation, target execution, automatic fixes or external scans |
| D-012 | AGENTS.md instructions separate from AGENT.md ledger | Retained; append-only session history preserved |
| D-013 | Bounded independent sub-agents with file ownership | Used for implementation, review and documentation |
| D-014 | Evidence-first fixture-only delivery | Owner approved after EGM/Astra review; completed |
| D-015 | AST now; Joern NOT_ATTEMPTED | Local Joern absent at inventory, no compatibility failure invented |
| D-016 | LS-AUTH-001 only; data/trust NOT_IMPLEMENTED | LOW-confidence declaration-gap candidates; opaque scopes diagnostic-only |
| D-017 | Exact scanned-byte manifest is authoritative | Includes policy identity; dirty/no-Git content cannot masquerade as clean commit |
| D-018 | Linear CLI/report workflow; no live egress | API/UI/LangGraph/providers remain future increments |
| D-019 | Local CPython 3.13.14 + locked Pydantic/NetworkX | Implemented local environment and backend/uv.lock; no global installs |
| D-020 | Process caps are not an OS hostile-repository sandbox | Only controlled local fixture approved; broader intake needs N14/N15 |

## Resolved first-session questions

- Repository exists with backend package/tests, synthetic fixture/oracle and docs; initial documentation-only discovery is complete. No `.git` directory has been initialized.
- Last observed machine/tool inventory is dated in AGENT.md; do not rerun all setup or silently treat historical versions as freshly measured.
- Astra/Sol delegated execution was exercised; Terra is available as a runtime choice but was not used for this backend slice. Coordinator display identity was not exposed.
- Supported FastAPI subset, opaque control behavior, byte evidence and CLI contract are frozen in document 13 and tested. The fixture graph/report pipeline is complete.
- Last verified baseline: 73 tests; 6 endpoints, 23 nodes, 36 edges, 2 LOW candidates and 3 matching declarations; expected PARTIAL coverage. This is not generalized detector accuracy.

## Remaining external facts and product choices

| Gate | Status / next action |
|---|---|
| Event acceptance, complete rules, team/track, required Meta usage | Owner-only portal facts unverified; N01 |
| Public deadline | Official page reopened Nov 2: Nov 4, 9:00 PM ET = Nov 5, 7:30 AM IST; may change |
| Actual Meta account/model access, quota, privacy/spend approval | Not verified by public documentation; N02/N08 |
| License, Git baseline, publication/deployment | No Git or license selected; N03; remote actions require separate selection |
| Next demo contract and team allocation | Proposed artifact viewer; no second human teammate assumed; N05/N06 |
| Joern/value-flow capability and trust policy | No measurements/implemented families; N09/N10 |
| Arbitrary-repository isolation/intake | Not approved or implemented; N14/N15 before expansion |

## Proposed follow-on choices — not new accepted decisions

R-001: resolve submission/provider requirements early and preserve the offline product independently of eligibility. R-002: fixed validated synthetic artifact viewer before HTTP/scan controls. R-003: optional explanation contract/mock before gated live Meta; schema-valid prose still needs review. R-004: timebox analyzer experiments and leave unsupported detectors explicit rather than consume demo buffer. R-005: local Git commit supplements content evidence; publication is separate. Astra reviewed this ordering; owner selection of an implementation increment is still required.

## Risks and stopping conditions

- Unknown/opaque controls can hide real problems; keep diagnostics and never label recognized declarations secure.
- Process/output prechecks do not protect against hostile concurrent filesystem changes; no arbitrary target expansion without a new isolation review.
- Valid evidence IDs do not establish factual model prose; keep facts immutable, review shown narrative, retain disabled/offline fallback.
- Provider/event access may block submission suitability while local software still works; record that distinction honestly.
- Avoid unfinished stack scaffolding: no obligatory API, LangGraph, new detector, database service or swarm just to match the original diagram.
- Keep measured revision/path evidence and independently review trust-boundary changes. Do not multiply severity, confidence and coverage into an unexplained score.

## Rejected or deferred directions

No universal compiler, complete-graph promise, automatic exploit validation/remediation, multi-language first increment, distributed graph database or microservice deployment without measured need. N14–N18 retain the longer-term analysis, intake, operational and platform backlog without pretending it is currently delivered.
