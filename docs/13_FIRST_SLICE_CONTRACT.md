# 13 — Evidence-first delivery contract

Approved by the owner on 2026-11-01 following consolidated EGM review and Astra architecture/security review. This contract takes precedence over broader MVP targets in documents 00–12 for the first delivery.

> Status refreshed 2026-11-02: this approved first slice is complete. See [verification evidence](14_IMPLEMENTATION_REVIEW.md) and [proposed remaining checklist](15_NEXT_STEPS.md). The later roadmap does not silently widen this contract. The separately approved [integrated demo contract](16_DEMO_DELIVERY_CONTRACT.md) adds exports, explanations and a fixed viewer; [document 19](19_INTEGRATED_DEMO_REVIEW.md) records its current verification. The exclusions below describe this historical first-slice milestone.

## Scope and acceptance

One controlled, repository-owned synthetic FastAPI fixture is analyzed without imports, execution, target dependency installation, network requests, or external model calls. The result is a reproducible normalized graph, authorization-context assessments, coverage diagnostics, SQLite metadata, and JSON/Markdown reports. No arbitrary repository intake, uploads, HTTP API, React UI, LangGraph, or live model integration is included.

The first slice implements **LS-AUTH-001 only**. LS-DATA-001 and LS-TRUST-001 are `NOT_IMPLEMENTED`; Joern is `NOT_ATTEMPTED`, because no local executable/POC has been measured. AST call relationships are never represented as value propagation or full CPG/taint analysis.

## Package and shared interfaces

- CPython 3.13.14; project-local uv environment and lockfile under `backend/`.
- Pydantic boundary models, NetworkX MultiDiGraph with stable edge IDs; standard-library AST, argparse, SQLite, JSON, and hashing. pytest, Ruff, and mypy are development dependencies. FastAPI is not needed to parse the fixture.
- Shared models in `backend/src/lazarus_sentinel/models.py` retain schema version `0.1.0` and the envelopes in document 03. Policy author/time provenance is recorded per protected operation.
- `load_snapshot(root: Path) -> Snapshot`; `verify_snapshot(root, snapshot) -> None`; `analyze(snapshot: Snapshot) -> Graph`; `analyze_snapshot(snapshot, timeout_seconds=30) -> Graph` runs extraction in a child process.
- Snapshot source files preserve exact bytes using base64 for worker transport. The revision hashes the sorted relative file/content manifest and policy identity. Git metadata, if available, is supplementary, never authoritative for dirty source.
- Endpoint properties: `handler_id`, HTTP `method`, effective `path`, exact qualified `dependencies`, and `control_scope_supported`. Observed dependencies use `DEPENDS_ON`, not assertions that authorization executes correctly.
- Findings retain `verification_status=CANDIDATE`, `triage_status=NEEDS_REVIEW`, and assessment `POTENTIAL_GAP`. `NEEDS_CONTEXT` belongs to diagnostics, not security findings.

## Supported source subset

Extract modules, classes, functions, imports, and unambiguous direct local calls, including uniquely resolved imported aliases. Resolve literal FastAPI app/router route decorators and a single, one-level inclusion of each router with literal prefixes. Collect explicit function dependencies from app, router, inclusion, decorator, default-value parameter, and `Annotated` parameter declarations (`Depends`/`Security`). A declaration is evidence of syntax, not enforcement.

Nested/repeated inclusion, implicit `Depends()`, dependency classes/factories/subdependencies, aliased or forward-string annotations and nonliteral/aliased parameter defaults, shadowing/rebinding, custom decorators, middleware, and dynamic registration are unsupported. Emit diagnostics and mark affected route/control scopes unknown. A separate dynamic route does not invalidate unrelated statically resolved routes; opaque application-wide middleware does affect their control scopes. Do not fabricate resolved call edges.

## Authorization truth table

The operator-authored `policy.json` identifies a protected operation and required authorization function by exact qualified symbol identity, with severity/impact assumption and author/time provenance. It is separate from the expected-results oracle, which the analyzer never reads.

| Supported structural path and control scope | Result |
|---|---|
| Matching policy-required declaration recognized | Suppress candidate; record declaration context with effectiveness unverified |
| Required declaration not identified in all supported dependency scopes | LOW-confidence `POTENTIAL_GAP` candidate; policy impact determines severity |
| Opaque control scope, ambiguous symbol, or unresolved structural path | `NEEDS_CONTEXT` diagnostic only |
| No policy-defined protected operation | No sensitivity/authorization guess and no candidate |

Authentication alone does not satisfy the authorization policy. Every candidate explains that external, imperative, and runtime controls have not been proven absent. No result is automatically confirmed or labeled secure.

## Intake, failure, and publication

- CLI: `lazarus scan --target fixture:fastapi-demo`; only that fixture ID is mapped. Internal root arguments exist for testing, not remote intake.
- A bounded `manifest.json` explicitly lists analyzed source paths. Maximum 100 Python files, 256 KiB per file, 5 MiB total scanned source; manifest and policy are bounded metadata. Reject traversal, symlinks, non-regular files, invalid manifests, and over-limit intake. No unbounded directory traversal or reads.
- Parse the immutable snapshot in a credential-free child with a 30-second total extraction deadline. Kill on deadline; do not retry. This is bounded execution, not an OS security sandbox or measured performance guarantee.
- Retain hashes and locations, not raw excerpts. Recheck source identity before evidence publication. Invalid intake/stale source/no usable graph is `FAILED`; useful results with relevant parser/unsupported gaps are `PARTIAL`.
- Unique output directories: `artifacts/scans/<scan_id>/`; database: `artifacts/sentinel.sqlite3`. Never overwrite prior scans. Stage artifacts and publish by atomic rename, then commit validated database references together. Readers use committed references. Interrupted work is failed, never automatically rerun.
- SQLite tables: scans, findings with composite `(scan_id, finding_id)` identity, and artifact references with `(scan_id, kind)` identity. No triage/API subsystem yet.
- stdout is one JSON summary containing `scan_id`, `status`, `artifact_dir`, `counts`, and `diagnostic_codes`. Exit 0 completed, 2 partial, 1 failed. Diagnostics exclude raw source, credentials, host paths, and stack traces.

## Verification gate

Require positive/recognized/authentication-only/public/unknown cases, inherited controls, alias/shadowing and duplicate symbols, unsupported registration, valid ordered evidence paths, source mutation, bounded intake/timeout, no target execution/network operations, deterministic repeat results, persistence/reload consistency, and safe reports. Run Ruff, mypy, pytest, then independent read-only Astra review. Implementation and submission readiness are separate gates.
