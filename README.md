# Lazarus Sentinel

Graph-first, evidence-backed application-security analysis. The implemented release is a **controlled synthetic FastAPI fixture scanner**, not an arbitrary-repository security audit.

## Current verified baseline — 2026-11-02

| Capability | Status |
|---|---|
| Intake | Fixed `fixture:fastapi-demo` identifier; manifest-bounded, read-only source parsing |
| Analysis | Python AST structure + supported literal FastAPI routes/dependencies; no target imports/execution |
| Graph | Schema 0.1.0, deterministic identities, NetworkX MultiDiGraph, source hashes/locations |
| Rule | LS-AUTH-001, LOW-confidence declaration-gap candidates; opaque controls are diagnostics only |
| Persistence/report | SQLite committed references; graph/findings/coverage JSON and escaped Markdown |
| Measured demo | 6 endpoints, 23 nodes, 36 edges, 2 candidates, 3 matching declarations with effectiveness unverified |
| Quality | Last verified: 73 tests; Ruff check/format clean; strict mypy clean on 11 source modules |
| Deferred | Joern POC, data/trust rules, UI/API, LangGraph, live LLM, arbitrary repositories and hostile-input isolation |

The fixture intentionally contains unsupported dynamic registration. Its normal outcome is **PARTIAL / exit 2**. A matching authorization declaration is syntax evidence, not proof of enforcement or a secure endpoint.

## Run locally

From this checkout's root, using the pinned CPython 3.13.14 toolchain:

```sh
uv sync --project backend --locked
uv run --project backend --locked lazarus scan --target fixture:fastapi-demo
```

stdout is one JSON summary. Exit 0 means the selected static profile completed without relevant coverage gaps; exit 2 means useful partial output; exit 1 means failure. Artifacts are written to `artifacts/scans/<scan_id>/{graph.json,findings.json,coverage.json,report.md}`. Metadata and committed artifact references are in `artifacts/sentinel.sqlite3`. Repeated scans do not overwrite each other. Evidence stores relative locations and hashes, not raw source excerpts.

Trusted implementation checks:

```sh
uv run --project backend --locked pytest backend/tests
uv run --project backend --locked ruff check backend/src backend/tests
uv run --project backend --locked ruff format --check backend/src backend/tests
uv run --project backend --locked mypy --config-file backend/pyproject.toml backend/src
```

If a restricted environment cannot use the shared uv cache, prefix uv commands with `UV_CACHE_DIR=/private/tmp/lazarus-uv-cache`. Do not manually delete shared caches. Installation is project-local; FastAPI is not needed to parse the synthetic target.

## What to do next

Follow the **[complete ordered checklist](docs/15_NEXT_STEPS.md)** and its mirrored [task board](TASK_BOARD.md). The recommended next milestone is a viewer of existing validated synthetic graph/findings/coverage artifacts. Check event acceptance and runtime-provider requirements immediately; then freeze the viewer/explanation contracts. HTTP services, new detectors and orchestration are not prerequisites for that demo.

Everything beyond the completed first slice is a recommendation awaiting its own selected scope. This documentation refresh does not initialize Git, install another dependency, enable model egress, build a UI, deploy, or submit anything.

## Documentation map and authority

1. [AGENTS.md](AGENTS.md): persistent safety/model/workflow instructions.
2. [AGENT.md](AGENT.md): live state and append-only session evidence; do not restart completed tasks.
3. [First-slice contract](docs/13_FIRST_SLICE_CONTRACT.md): approved implemented scope.
4. [Implementation/review summary](docs/14_IMPLEMENTATION_REVIEW.md): measured results and limitations.
5. [Next steps](docs/15_NEXT_STEPS.md): recommended remaining work, dependencies, owners and exit criteria.
6. [Task board](TASK_BOARD.md): completed baseline and remaining task IDs.
7. [Continuation prompt](CODEX_BOOTSTRAP_PROMPT.md): handoff to a fresh agent.

Reference specifications distinguish current implementation from future capability:

- [00 Charter](docs/00_PROJECT_CHARTER.md), [01 Requirements](docs/01_REQUIREMENTS.md), [02 Architecture](docs/02_ARCHITECTURE.md), [03 Graph schema](docs/03_GRAPH_SCHEMA.md), [04 Rules](docs/04_ANALYSIS_RULES.md).
- [05 Orchestration](docs/05_ORCHESTRATION.md), [06 API/persistence](docs/06_API_AND_PERSISTENCE.md), [07 Frontend](docs/07_FRONTEND.md), [08 Security](docs/08_SECURITY_MODEL.md), [09 Evaluation](docs/09_TESTING_EVALUATION.md).
- [10 Roadmap](docs/10_IMPLEMENTATION_PLAN.md), [11 Decisions/assumptions](docs/11_DECISIONS_AND_ASSUMPTIONS.md), [12 Source register](docs/12_SOURCES.md).

## Boundaries

Only the fixed owned fixture is accepted. Intake caps are 100 Python files, 256 KiB/file, 5 MiB total; a credential-free parser child has a 30-second deadline. These are process/input limits, **not an OS filesystem/network sandbox**. Hostile concurrent filesystem replacement is outside scope. No target code is executed, no runtime security is established, and no source/model request is sent externally by this release.

Joern is NOT_ATTEMPTED; LS-DATA-001 and LS-TRUST-001 are NOT_IMPLEMENTED. No Git repository has been initialized, no license has been selected, and nothing has been committed, published or submitted. Generated scan reports are historical evidence; use new scan identities rather than editing old results.
