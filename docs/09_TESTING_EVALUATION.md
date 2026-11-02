# 09 — Testing, Evaluation and Evidence Quality

## Integrated demo status — 2026-11-02

The approved [demo contract](16_DEMO_DELIVERY_CONTRACT.md) is implemented alongside the preserved first-slice analyzer: immutable hash-verified bundles, disabled/mock explanations with a gated Meta adapter, and a fixed React/Vite/TypeScript/Cytoscape viewer. See [capability gates](17_CAPABILITY_AND_RESEARCH_REPORT.md), [finite evaluation](18_DEMO_EVALUATION.md), and [integrated verification](19_INTEGRATED_DEMO_REVIEW.md) for current checks and review disposition. Document 14 remains historical first-slice evidence; its 73-test count is not the integrated total.

Local baseline commit `7797b85` is preserved on `feat/integrated-demo`; no remote, publication, submission or license selection is implied. Only fixed synthetic intake is supported. Live access is BLOCKED by the missing key; zero paid calls were made. Joern setup is blocked and analysis NOT_ATTEMPTED; data/trust rules remain NOT_IMPLEMENTED. OS sandbox launch failed before execution, so broader intake remains blocked.

## Verified baseline (2026-11-02)

The implementation review and machine-readable verification record 73 passing backend tests, clean Ruff check/format (21 files) and strict mypy (11 source modules). Two fixture scans produced identical complete graph JSON: six supported endpoints, 23 nodes, 36 edges, two LOW-confidence candidates and three matching declarations with effectiveness unverified. Dynamic registration intentionally yields PARTIAL and CLI exit 2.

This establishes the tested controlled-fixture behavior and evidence/artifact integrity. It does not establish generalized precision/recall, external-tool superiority, runtime reachability, authorization effectiveness, exploitability, operational scale or arbitrary-repository safety.

## Existing verification scope

Tests cover deterministic IDs/graphs, exact source-byte/range validation, supported routes/dependency scopes, policy-defined positive and negative cases, authentication-only/public cases, ambiguous/opaque scope suppression, aliases/shadowing/duplicates, unsupported constructs, bounded intake/timeouts, source mutation, safe report rendering, persistence and committed artifact consistency. Independent Astra review included uncertainty probes and behavior-preservation controls; see the implementation review for provenance.

The checked-in synthetic fixture and separate expected-results oracle are current, not work still to create. Analysis reads policy but not the oracle. Local baseline commit 7797b85 supplements the authoritative content-manifest revision including policy. Current reports retain evidence hashes/locations without snippets.

## Reproduce

From the project root with the existing project-local environment:

```sh
uv run --project backend --locked pytest backend/tests
uv run --project backend --locked ruff check backend/src backend/tests
uv run --project backend --locked ruff format --check backend/src backend/tests
uv run --project backend --locked mypy --config-file backend/pyproject.toml backend/src
uv run --project backend --locked lazarus scan --target fixture:fastapi-demo
```

The scan's expected exit 2 must not be treated as an unexpected failure or retried automatically. New scans use unique IDs; compare normalized graph JSON and validated source/artifact hashes, not directory names or scan timestamps. Commands/results above are the recorded baseline; this documentation refresh does not claim a fresh code/test run.

## Requirements for future detector changes

Include a positive case, safe negative case and incomplete/unknown case with expected status/confidence and source/path evidence. Preserve declaration-versus-enforcement limits. New analyzer capability needs supported syntax coverage, failure/timeout handling, deterministic results and evidence validation before broader claims.

Joern, Semgrep and CodeQL comparisons have not run. Data-flow/trust rules, HTTP API, LangGraph, archive isolation and multi-user behavior have no implemented feature coverage. Bundle integrity, provider schemas/disabled/mock/failure/budget behavior and fixed UI paths have integrated tests recorded in document 19. Their tests belong with selected future increments; do not list them as existing integration suites.

## Future evaluation proposals

Use declared benchmark denominators for endpoint extraction, path accuracy, evidence completeness, unsupported scope and seeded candidate outcomes. Measure latency/resource use against declared workloads. Model factuality/egress tests apply only after a provider increment exists. Verify external benchmark language/license fit before adoption and compare like-for-like tool configurations. Qualitative confidence labels are not calibrated probabilities, and synthetic outcomes must remain visibly scoped.
