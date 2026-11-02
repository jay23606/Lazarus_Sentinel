# Evidence-first implementation — verified 2026-11-02

The owner-approved controlled fixture slice is implemented. This is a scoped static declaration assessment, not an audit of arbitrary repositories or proof of runtime security.

> This document records the verified baseline; the [complete next-step checklist](15_NEXT_STEPS.md) and [task board](../TASK_BOARD.md) describe remaining work. A documentation refresh does not imply these tests or live provider checks were rerun.

## Measured result

| Item | Verified result |
|---|---|
| Supported endpoints | 6 |
| Graph | 23 nodes / 36 edges |
| Authorization-context candidates | 2: GET /weak and GET /authenticated |
| Policy-matching declarations | 3; effectiveness unverified |
| Public/no-policy path | No finding |
| Seeded dynamic registration | NEEDS_CONTEXT / partial coverage |
| Scan outcome | PARTIAL, expected CLI exit 2 |
| Repeat scans | Exact graph JSON match |
| Evidence / persistence | Source ranges and hashes, committed artifact sizes and SHA256 validated |
| Tests | 73 passed |
| Ruff | Check and format clean, 21 files |
| mypy | Strict checks clean, 11 source modules |

[Generated report](../artifacts/scans/0ab604f2-f6f3-458e-9665-44c426f9b98f/report.md) · [Machine-readable verification](../artifacts/verification.json) · [Run instructions](../README.md)

Revision: `revision:sha256:b9cbcb3c59a1e4220ef42f5dcf5dea3a482e364f9907cfd6d5d81fe33ee9d49d`. Latest scan: `0ab604f2-f6f3-458e-9665-44c426f9b98f`.

## Review and repairs

Sol implemented bounded, separately owned core/extraction/application tasks. Astra independently reviewed the integrated implementation, reran the suite and 17 false-candidate probes, verified two intended-behavior control probes, and approved the controlled scope. A later report-only change adds escaped endpoint names, ordered paths and declared dependencies; Astra approved that display change separately.

Regression repairs conservatively handle subdependencies, aliased/string annotations and defaults, middleware/constructor hooks, non-top-level inclusion, symbol rebinding/deletion/duplication, colliding module names, intermediate opaque path scopes and source/output symlinks. Unsupported control scopes do not produce security candidates. Exact source-byte evidence is checked before publication.

Initial scaffolding could not achieve behavioral RED while pytest was unavailable; that workflow limitation is recorded rather than presented as test-first evidence. Later material review regressions were observed failing before their repairs.

## Reproduce

From the project root:

```sh
uv sync --project backend --locked
uv run --project backend --locked lazarus scan --target fixture:fastapi-demo
uv run --project backend --locked pytest backend/tests
uv run --project backend --locked ruff check backend/src backend/tests
uv run --project backend --locked ruff format --check backend/src backend/tests
uv run --project backend --locked mypy --config-file backend/pyproject.toml backend/src
```

The scan intentionally exits 2 for seeded partial coverage. Package installation is project-local, and backend/uv.lock records exact versions/hashes. No Git repository was initialized and nothing was committed or published.

## Limits and deferred work

AST call relationships are syntax evidence, not runtime reachability, authorization effectiveness or data flow. Unknown suppression can miss candidates. Sanitized environment, deadlines and process limits are not an OS network/filesystem sandbox; concurrent hostile filesystem mutation remains outside scope. A crash between rename and database commit can leave orphan files, but readers use committed artifact references only.

Joern is NOT_ATTEMPTED; LS-DATA-001 and LS-TRUST-001 are NOT_IMPLEMENTED. Arbitrary repository/upload intake, API/UI, LangGraph, live model providers, external validation and hackathon submission readiness remain deferred/unverified. No target code was executed and no live model calls were made.

## Documentation reconciliation — 2026-11-02

All 21 maintained Markdown documents now separate delivered behavior from proposed next work. Relative links, JSON examples, code fences, documentation manifest coverage and N01–N18 task mirroring validated. Backend source/test/Python-fixture/dependency fingerprints were unchanged. This documentation-only check does not replace or repeat the 73-test implementation verification above. Follow [document 15](15_NEXT_STEPS.md) for the complete recommended sequence; no follow-on feature is started implicitly.
