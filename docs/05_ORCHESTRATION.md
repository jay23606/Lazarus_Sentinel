# 05 — Scan Orchestration

## Integrated demo status — 2026-11-02

The approved [demo contract](16_DEMO_DELIVERY_CONTRACT.md) is implemented alongside the preserved first-slice analyzer: immutable hash-verified bundles, disabled/mock explanations with a gated Meta adapter, and a fixed React/Vite/TypeScript/Cytoscape viewer. See [capability gates](17_CAPABILITY_AND_RESEARCH_REPORT.md), [finite evaluation](18_DEMO_EVALUATION.md), and [integrated verification](19_INTEGRATED_DEMO_REVIEW.md) for current checks and review disposition. Document 14 remains historical first-slice evidence; its 73-test count is not the integrated total.

Local baseline commit `7797b85` is preserved on `feat/integrated-demo`; no remote, publication, submission or license selection is implied. Only fixed synthetic intake is supported. Live access is BLOCKED by the missing key; zero paid calls were made. Joern setup is blocked and analysis NOT_ATTEMPTED; data/trust rules remain NOT_IMPLEMENTED. OS sandbox launch failed before execution, so broader intake remains blocked.

## Implemented linear workflow

`service.scan()` coordinates a single controlled fixture scan:

1. Validate the exact fixture target and initialize the safe artifact store.
2. Acquire the single-writer lock and mark interrupted RUNNING scans FAILED.
3. Load bounded manifest/policy/source bytes and compute the immutable content revision.
4. Send the snapshot to the AST child worker with a 30-second extraction deadline.
5. Add policy provenance, evaluate LS-AUTH-001 and record deferred analyzers/rules.
6. Validate ordered graph/evidence references against exact snapshot bytes.
7. Derive PARTIAL/COMPLETED from relevant coverage gaps; stage JSON and Markdown artifacts.
8. Recheck source, rename the unique artifact directory, recheck source again and commit results/reference hashes in SQLite.
9. Emit one JSON summary; never automatically retry failed work.

CLI final outcomes are COMPLETED (exit 0), PARTIAL (exit 2) and FAILED (exit 1). RUNNING is an internal ledger state. QUEUED/CANCELLED, cancellation/resume APIs and background job scheduling are not implemented. The seeded fixture normally exits 2 because dynamic registration is unsupported.

## Bounds and failure behavior

The worker accepts at most 8 MiB serialized input and 16 MiB output. It has CPU limit 25 seconds, file-size output bound and 64 open-file limit; the coordinator enforces the 30-second total deadline and kills on timeout. These are defensive bounds, not measured latency guarantees or filesystem/network isolation. No target code import/execution or provider call is part of this pipeline.

Invalid intake, stale evidence/source, unusable graph or publication failure produces FAILED with safe codes. Useful results with relevant unsupported/parser gaps produce PARTIAL. LS-DATA-001/LS-TRUST-001 are NOT_IMPLEMENTED and Joern is NOT_ATTEMPTED; their explicit NOT_ATTEMPTED coverage entries alone do not force PARTIAL. The transaction publishes committed references together; orphan directories can remain after an interrupted rename-to-commit interval.

## Future LangGraph workflow — deferred proposal

LangGraph is neither installed nor required for first-slice completion. If later justified by measured concurrency/state needs, map the existing deterministic stages into typed nodes and explicit transitions while preserving evidence gates, bounded failure handling and no automatic duplicate analysis. Any parallel analyzer branches require agreed immutable inputs and merge contracts first.

The separate `explain` command is optional enrichment after deterministic evidence validation, with provider/privacy/output gates; it is not a LangGraph node. Durable checkpoints, user pause/resume, cancellation, retries, streaming and API job queues are future design questions rather than current interfaces.
