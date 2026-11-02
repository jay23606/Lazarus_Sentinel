# 06 — CLI, Artifacts, API Roadmap and Persistence

Current implementation is governed by the [approved first-slice contract](13_FIRST_SLICE_CONTRACT.md). [Verified results](14_IMPLEMENTATION_REVIEW.md) describe the measured fixture run; [ordered next steps](15_NEXT_STEPS.md) are proposals for subsequent work, not approval to implement them.

## Implemented command

From the project root after the project-local environment is synced:

```sh
uv run --project backend --locked lazarus scan --target fixture:fastapi-demo
```

Only `scan --target fixture:fastapi-demo` is supported. There are no report/export/findings subcommands, `--profile`, HTTP endpoints, uploads or arbitrary repository paths. The current internal profile is `reduced-static-auth`.

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
