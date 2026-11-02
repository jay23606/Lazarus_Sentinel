# 18 — Controlled demo evaluation and reproducibility

QA measurement dated **2026-11-02**. The baseline and added cases are synthetic source-level declaration assessments. Results do not estimate production detection accuracy, runtime authorization effectiveness, exploitability, or arbitrary-repository isolation. Integrated UI/provider acceptance and final Astra review belong to the coordinator; this report records this bounded QA tranche.

## Corpus and predeclared expectations

The original controlled fixture and its separate oracle remain unchanged. A second independent corpus is under `fixtures/evaluation_variants/authorization_context/`; its expected-results oracle is **outside** the intake root at `fixtures/evaluation_variants/oracle.json`. The oracle was written before the first analysis, and is never passed to the analyzer. The initial new test failed because the new fixture manifest did not yet exist, then passed after the fixture was added. No analyzer/rule source was changed to satisfy it.

The new target intentionally raises `RuntimeError("STATIC_PARSE_ONLY: fixture must never execute")` at module level. Parsing succeeds without importing or executing it; the fixture's FastAPI dependency is not installed or imported for evaluation. Only the trusted application tests and analyzer implementation run.

| Corpus / scenario | Predeclared expected result | Measured result |
|---|---|---|
| Baseline GET /weak | One LOW candidate to protected export operation | Exact endpoint/path matched |
| Baseline GET /authenticated | Authentication declaration does not satisfy authorization policy | One LOW candidate, exact endpoint/path matched |
| Baseline GET /protected, /annotated, /inherited/export | Matching declaration; effectiveness unverified | Three declarations; no candidates for those endpoints |
| Baseline GET /public | No sensitivity policy | No finding |
| Baseline dynamic registration | Unsupported registration context | Diagnostic/partial coverage; not counted as a detected weakness |
| Added GET /gap | One LOW candidate through supported handler/service/operation | One candidate; terminal `app.repository.export_records` |
| Added GET /declared | Exact `app.controls.authorize_export` dependency | Recognized declaration; no candidate; effectiveness unverified |
| Added GET /unknown | Opaque helper decorator on structural path | NEEDS_CONTEXT diagnostic; no candidate |

Denominators: baseline **6 statically supported endpoints**, **2 expected candidate endpoints**, **3 declaration comparisons**, **1 no-policy endpoint**, plus **1 separately unsupported dynamic registration**. Added corpus: **3 endpoints**, **1 expected candidate**, **1 declaration comparison**, **1 unknown path**. Across both corpora the **3/3 predeclared candidate endpoints** matched, **4/4 declared comparisons** suppressed candidates, **1/1 unknown added path** suppressed candidates, and **1/1 baseline public endpoint** produced none. These are exact synthetic contract matches, not sensitivity/specificity claims or an untouched benchmark. Unknown suppression can hide real weaknesses.

## Repeat/evidence measurements

Two baseline application-service scans used fresh temporary artifact roots, unique scan IDs, real bounded extraction workers and database/artifact publication. Two added-corpus repetitions used immutable intake → AST extraction → authorization evaluation → exact evidence-byte validation directly; they are not extra supported CLI targets. Temporary outputs were discarded by the test harness, not by the production inspector. No original persisted scan was rewritten.

| Measurement | Baseline repetitions | Added-corpus repetitions |
|---|---|---|
| Endpoints / nodes / edges | 6 / 23 / 36 | 3 / 15 / 22 |
| Candidates | 2 / 2 | 1 / 1 |
| Status or diagnostics | PARTIAL both; seeded unsupported registration | Recognized declaration + NEEDS_CONTEXT both |
| Wall time, seconds | 0.1002 / 0.1078 | 0.0023 / 0.0018 |
| Repeat graph identity | Exact persisted graph JSON bytes equal | Exact deterministic model serialization equal |
| Source verification | Before publication; artifact hashes checked | Every evidence range/hash recomputed from snapshot; final snapshot identity rechecked |

Baseline graph SHA256: `733143b600d67402632a7e519539e2d8ec666ea655b2857c460bead15fccba55`.

Added-corpus graph SHA256 using `Graph.model_dump_json()` UTF-8 bytes: `04662f91ece7bf778f4547c6848dff620b95a6f3b6bcd0ba4aa6eb4b1274c210`.

The serialization encodings differ, so compare each hash only within its own column. Times are two warm local runs on this Mac, include different stages, and are not a scale benchmark, cold-start SLA or cross-adapter comparison. CPU/RSS/process/network isolation was not measured here. See [capability report](17_CAPABILITY_AND_RESEARCH_REPORT.md) for the blocked sandbox and analyzer gates.

## Read-only operations inspection

`scripts/inspect_artifacts.py` is a standalone standard-library diagnostic. It opens the existing SQLite file with **`mode=ro`** and `PRAGMA query_only=ON`; it never constructs the mutating application Store, recovers RUNNING rows, retries jobs, creates a database, deletes artifacts or repairs corrupt data. It checks database integrity, bounded rows/file sizes, committed scan states, expected reference kinds, relative paths, symlinks, exact artifact hashes/sizes and JSON readability. Unknown/uncommitted/staging directories are reported for human review.

A read-only inspection during this tranche returned **6 scans, 24 committed references, 24 verified artifacts, zero issues**, `mutations:false`. Counts are a dated local snapshot, not an invariant of future runs.

The regression test creates its own temporary scan, verifies clean inspection, adds an orphan directory and corrupts one graph's bytes. Inspection reports both anomalies while database bytes and the orphan/corrupt files remain unchanged. `RUNNING` is reported as interrupted **or active**: a read-only inspector cannot safely infer which. It never decides to kill/retry a process.

```sh
uv run --project backend --locked python scripts/inspect_artifacts.py
```

Exit codes: `0` OK, `2` issues requiring review, `1` inspection failed. The optional `--root` is a trusted operator diagnostic input, not an application target/intake API. The inspector does not authenticate artifacts against an external signer, prove graph semantics or protect against concurrent hostile host filesystem mutation; use the application bundle loader for semantic/source-bound demo export. It makes no changes to orphan policy or retention.

## Reproducibility checks and CI

```sh
uv sync --project backend --locked
npm ci --prefix frontend --ignore-scripts --no-audit --no-fund
uv run --project backend --locked python scripts/verify_demo.py
```

`verify_demo.py` runs trusted backend tests, Python lint/format/type checks, frontend typecheck/lint/tests/build, and validates the shipped fixed synthetic bundle through the backend's bundle contract. It checks actual manifest-plus-payload byte bounds. It uses a minimal subprocess environment, makes no provider request, and outputs a JSON list of per-check status/exit/time. A missing/invalid bundle or missing frontend toolchain fails verification; it is never presented as an empty successful graph. Install/sync is explicit and separate from verification; neither script installs target dependencies or runs target build scripts.

`.github/workflows/ci.yml` provides the same credential-free offline checks on GitHub-hosted Ubuntu: Python 3.13.14, uv 0.12.5, Node 24.14.0, locked Python/npm dependencies, read-only repository permissions, no persisted checkout credentials, no provider secret inputs, no publish/deploy step, no target repository supplied. Dependencies/actions require network for setup; **offline** here describes the analysis/provider behavior after setup, not a promise of air-gapped dependency installation. Hosted CI has not been run by this local QA task.

Action inputs were verified against official [checkout](https://github.com/actions/checkout), [setup-node](https://github.com/actions/setup-node) and [setup-uv](https://github.com/astral-sh/setup-uv) documentation. uv's setup action is commit-pinned; checkout/setup-node use their published v7 major tags. Review/update action pins as a separate maintenance decision rather than silently claiming immutability for mutable major tags.

## Verification snapshot and remaining integration work

- New evaluation/inspector test module: **2 tests pass**, 0.26 seconds pytest time / 0.38 seconds external wall time on the recorded run.
- Full backend suite at this tranche's measurement: **114 passed in 3.80 seconds**. Other agents were adding independent bundle/explanation tests concurrently; this is a dated count, not the final integrated count.
- Owned Python scripts/test pass Ruff check/format. Strict mypy passes when checked with the backend source tree (18 source files at that check); no type-stub package was added.
- The first integrated `verify_demo.py` run correctly **failed** while the shipped frontend bundle was not yet copied and parallel source files were still being formatted. Backend tests/types and all four frontend commands passed in that run. This is incomplete integration, not a successful final verification. The coordinator must rerun after handoff and record the resulting final counts/bundle/browser/Astra checks.
- Inspector read-only/orphan/corruption behavior was tested; hosted CI, clean foreign host setup, backup/restore, large-corpus performance, live provider use, Joern execution and hostile-source isolation remain unverified or blocked. No automatic fix, network scan, deployment, publication or submission occurred.
