# 06 — CLI, Artifacts, API Roadmap and Persistence

> Team/platform update (2026-11-02): [team handoff](21_TEAM_HANDOFF.md), [finite next-phase plan](22_NEXT_PHASE_PLAN.md), and [current portability/publication evidence](23_PORTABILITY_AND_RELEASE_VERIFICATION.md) supersede earlier onboarding, remote-state and platform assumptions. Historical checks below retain their original date and scope.


## Integrated demo status — 2026-11-02

The approved [demo contract](16_DEMO_DELIVERY_CONTRACT.md) is implemented alongside the preserved first-slice analyzer: immutable hash-verified bundles, disabled/mock explanations with a gated Meta adapter, and a fixed React/Vite/TypeScript/Cytoscape viewer. See [capability gates](17_CAPABILITY_AND_RESEARCH_REPORT.md), [finite evaluation](18_DEMO_EVALUATION.md), and [integrated verification](19_INTEGRATED_DEMO_REVIEW.md) for current checks and review disposition. Document 14 remains historical first-slice evidence; its 73-test count is not the integrated total.

Baseline commit `7797b85`, integrated demo `4f0346c` and viewer refinement `2cda191` are preserved on `feat/integrated-demo`. Publication to the owner-specified repository is now authorized; actual remote/CI outcomes are recorded in document 23. License and submission decisions remain unresolved. Only fixed synthetic intake is supported. Live access is BLOCKED by the missing key; zero paid calls were made. Joern setup is blocked and analysis NOT_ATTEMPTED; data/trust rules remain NOT_IMPLEMENTED. OS sandbox launch failed before execution, so broader intake remains blocked.

## Implemented command

From the project root after the project-local environment is synced:

```sh
uv run --project backend --locked lazarus scan --target fixture:fastapi-demo
```

Scanning still accepts only `fixture:fastapi-demo`. The CLI additionally supports `demo export --scan-id <UUID> [--annotation-id <UUID>]` and `explain --scan-id <UUID> --finding-id <ID> [--provider disabled|mock|meta]` (default disabled). There are no HTTP endpoints, uploads or arbitrary repository intake paths. The current internal profile is `reduced-static-auth`.

stdout is one JSON summary including scan_id, status, artifact_dir, counts and diagnostic_codes; successful scan processing additionally records schema/profile/revision/timestamps. Exit 0 means COMPLETED, 2 PARTIAL and 1 FAILED. Invalid arguments and internal failures return safe codes without echoing untrusted exception text. See README for setup and the implementation review for verified commands.

## Implemented artifacts and tables

Each scan writes `artifacts/scans/<scan_id>/graph.json`, `findings.json`, `coverage.json` and `report.md`. Graph JSON includes findings as well as structure/evidence/coverage/diagnostics. Coverage JSON also includes diagnostics. No report.json, SARIF or JSONL output is currently generated. Evidence retention is hash/location only, and Markdown escapes displayed labels.

Database: `artifacts/sentinel.sqlite3`.

| Table | Current fields / identity |
|---|---|
| scans | scan_id primary key, status, summary JSON |
| findings | scan_id + finding_id composite primary key, body JSON |
| artifact_refs | scan_id + kind composite primary key, relative path, sha256, size |

`Store.get(scan_id)` reads committed summary and artifact references. There are no projects, analyzer_runs, triage_events, provider-review or user/tenant tables. `triage_status=NEEDS_REVIEW` is a fixed finding field, not an editable triage subsystem.

The writer uses a filesystem lock, recovers interrupted RUNNING ledger entries as FAILED and never automatically reruns them. Artifacts are renamed before one results/reference transaction. Crash orphans can exist; only committed references are exposed. Concurrent hostile filesystem changes are not covered by the existing-alias prechecks.

## Future HTTP API — proposed, not implemented or frozen

A later API could expose controlled scan creation, scan summary, graph neighborhood/path queries, coverage, finding detail and report download. Human triage requires authenticated actor/rationale/revision tracking and reviewed persistence changes. An upload service requires a new isolation/intake contract before implementation.

Earlier `/api/v1/...` routes and request fields were sketches, not available endpoints. Freeze concrete routes, pagination, errors, auth and ownership against the selected next increment before frontend implementation. Avoid arbitrary host paths and large whole-graph responses. SARIF is optional later work requiring schema/consumer verification.
