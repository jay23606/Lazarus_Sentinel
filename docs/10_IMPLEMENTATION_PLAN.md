# 10 — Current delivery and remaining roadmap

Updated **2026-11-02**. The first slice in document 13 is complete; document 14 records its verification. The canonical actionable checklist is **[15_NEXT_STEPS.md](15_NEXT_STEPS.md)**, mirrored by [TASK_BOARD.md](../TASK_BOARD.md). Future work below is recommended, not implemented or automatically authorized.

## Completed baseline

- Fixed synthetic FastAPI fixture, bounded immutable byte intake, AST structure/dependency extraction.
- Schema 0.1.0 evidence graph, exact locations/hashes and deterministic identities, NetworkX MultiDiGraph.
- LS-AUTH-001 declaration-context candidates, unknown diagnostics, evidence gate, SQLite and JSON/Markdown reports.
- Last verified 73 tests, clean Ruff/strict mypy; 6 endpoints, 23 nodes, 36 edges, 2 LOW-confidence candidates and 3 matching declarations with effectiveness unverified.
- Expected demo PARTIAL/exit 2; no Git, UI/API, live provider, Joern POC, data/trust rules or OS hostile-repository sandbox.

## Recommended order

| Priority | Task IDs | Outcome |
|---|---|---|
| Immediate external gates | N01–N02 | Confirm owner acceptance/rules/deadline and authorized provider capability; do not discover access blockers at submission time |
| Baseline and contract | N03–N05 | Local version control/reproducibility, predeclared evaluation cases and next-increment interface/cut line |
| Demo experience | N06–N08 | Fixed artifact graph/findings/coverage viewer; offline explanation boundary; live Meta only after access/privacy/event gates |
| Optional capability work | N09–N11 | Timeboxed analyzer POC; separately gated data/trust rules; local read-only API only if needed |
| Release | N12–N13 | Integrated evaluation, independent review, freeze, reproducible demo and actual portal confirmation |
| Product expansion | N14–N18 | Isolation before broader intake, stronger semantics, operational/API features, additional languages/platforms |

See document 15 for each step's owner, prerequisites, tests and exit criteria. Do not put Joern setup, new detectors, scan-start controls, HTTP or LangGraph on the critical path merely to fill the original architecture diagram.

## Timing and submission gates

The [public event page](https://dev.meta.ai/events/global-hackathon), reopened **2026-11-02**, lists submissions due **November 4, 2026, 9:00 PM ET**, corresponding to **November 5, 2026, 7:30 AM IST**. Dates may change; owner acceptance and the actual portal rules remain unverified. A functioning offline demo is not proof of eligibility or required Meta use.

Proposed schedule, subject to owner confirmation:

| Date (IST) | Target |
|---|---|
| Nov 2 | Resolve external gates, baseline/fixture review, freeze next demo contract, start bounded artifact viewer |
| Nov 3 | Complete usable viewer and explanation boundary; live synthetic provider check/integration only if authorized and available |
| Nov 4 before 18:00 | Integration/evaluation, security review, clean setup and feature freeze |
| Nov 4 by 23:30 | Target submission and save portal receipt; retain contingency before the public deadline |
| Nov 5 early | Submission contingency only, no planned major implementation |

These are planning targets, not evidence that work is finished. If a provider/event gate is blocked, record it and reassess submission suitability. Keep an honestly labeled offline CLI/report/artifact fallback.

## Workstreams and scope cuts

A second human teammate is not confirmed. If available, split artifact/UI work from provider/evaluation work only after contracts freeze. Otherwise work serially; use bounded, separately owned sub-agents where useful. Astra owns critical judgments, Sol routine code/research and Terra UI.

Freeze the smallest useful demo first. Keep LS-DATA-001/LS-TRUST-001 visibly NOT_IMPLEMENTED unless their individual capability, policy and evaluation gates pass. Defer arbitrary repositories/uploads, HTTP scan execution, human triage writes, distributed storage, agent swarms, orchestration replacement and language expansion.

## Longer-term completion map

Document 15 N14–N18 covers tested isolation/retention; allowlisted local/archive intake; more framework and data-flow semantics; authorization ownership/tenant analysis; advisory/config/secrets correlations; read-only API then lifecycle/triage/pagination; crash recovery/incremental scans/SARIF/CI/packaging; justified LangGraph use; remote access/tenant isolation; further language, IaC/IAM and authorized telemetry adapters. No automatic exploitation or remediation is planned.
