# Lazarus Sentinel

Graph-first, evidence-backed application-security analysis. The implemented release is a **controlled synthetic FastAPI fixture scanner**, not an arbitrary-repository security audit.

For teammates, start with the [portable setup and module guide](docs/21_TEAM_HANDOFF.md), [contribution workflow](CONTRIBUTING.md), [next-phase plan](docs/22_NEXT_PHASE_PLAN.md), and [latest platform/publication evidence](docs/23_PORTABILITY_AND_RELEASE_VERIFICATION.md). Codex reads [AGENTS.md](AGENTS.md); Claude Code has a [CLAUDE.md](CLAUDE.md) entry point.

## Current demo — 2026-11-02

| Capability | Status |
|---|---|
| Intake | Fixed `fixture:fastapi-demo` identifier; manifest-bounded, read-only source parsing |
| Analysis | Python AST structure + supported literal FastAPI routes/dependencies; no target imports/execution |
| Graph | Schema 0.1.0, deterministic identities, NetworkX MultiDiGraph, source hashes/locations |
| Rule | LS-AUTH-001, LOW-confidence declaration-gap candidates; opaque controls are diagnostics only |
| Persistence/report | SQLite committed references; graph/findings/coverage JSON and escaped Markdown |
| Measured demo | 6 endpoints, 23 nodes, 36 edges, 2 candidates, 3 matching declarations with effectiveness unverified |
| Quality | [Current release](docs/23_PORTABILITY_AND_RELEASE_VERIFICATION.md): native Windows/macOS/Linux CI passed; local139backend tests plus oneWindows-only skip,16frontend tests |
| Demo | Hash-verified immutable bundle, disabled/mock explanation sidecars, fixed React/Cytoscape viewer; Meta adapter tested offline |
| Blocked/deferred | Live Meta access, Joern setup, data/trust rules, HTTP API, LangGraph, arbitrary repositories and OS isolation |

The fixture intentionally contains unsupported dynamic registration. Its normal outcome is **PARTIAL / exit 2**. A matching authorization declaration is syntax evidence, not proof of enforcement or a secure endpoint.

## Platform support

Native **Windows, macOS and Ubuntu/Linux** clean installation, tests and build passed in [GitHub Actions](https://github.com/sumitjadhav1703/Lazarus_Sentinel/actions/runs/41492178925). Use the same uv/npm commands below in macOS Terminal or Windows PowerShell. This is a local CLI/browser application; no desktop installer is provided.

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

If a restricted environment cannot use the shared uv cache, use the platform-specific writable-cache instructions in [document 21](docs/21_TEAM_HANDOFF.md). Do not manually delete shared caches. Installation is project-local; FastAPI is not needed to parse the synthetic target.

## View the integrated demo

```sh
npm ci --prefix frontend --ignore-scripts --no-audit --no-fund
npm run dev --prefix frontend
```

The viewer loads only the reviewed synthetic bundle in `frontend/public/demo/v1/`; use the loopback URL printed by Vite. Start with the three-step guide, search an endpoint, and inspect a focused path with readable node types and labeled arrows. Switch to Full graph for all relationships; select a node to inspect its source evidence. Fit/zoom/reset, keyboard step controls and expandable identity tables support deeper review. See the [viewer design and verification](docs/20_VIEWER_CLARITY_AND_DESIGN.md). No upload, source path input or HTTP backend is involved.

To create new immutable artifacts, substitute IDs returned by your own scan (finding IDs are in its findings.json):

```sh
uv run --project backend --locked lazarus demo export --scan-id <SCAN_UUID>
uv run --project backend --locked lazarus explain --scan-id <SCAN_UUID> --finding-id <FINDING_ID>
uv run --project backend --locked lazarus explain --scan-id <SCAN_UUID> --finding-id <FINDING_ID> --provider mock
uv run --project backend --locked lazarus demo export --scan-id <SCAN_UUID> --annotation-id <ANNOTATION_UUID>
```

Explanation defaults to DISABLED. Mock output is offline and unreviewed assistance; it never changes canonical findings. The Meta adapter requires explicit selection and reviewed access/privacy/budget gates; live verification is BLOCKED by the missing key, with zero paid calls. The application cap is USD3 and five live attempts, without retries. Do not treat mock operation as live API verification.

The shipped dataset uses scan `d4788c12-b956-4535-b897-13744439093e`, bundle `f85376c4-9ec1-4b8f-aea2-1c0f89abae3e`, and a recorded mock annotation. See [demo contract](docs/16_DEMO_DELIVERY_CONTRACT.md), [capability report](docs/17_CAPABILITY_AND_RESEARCH_REPORT.md), [finite evaluation](docs/18_DEMO_EVALUATION.md), and [integrated review](docs/19_INTEGRATED_DEMO_REVIEW.md). [Every N01–N18 disposition](docs/15_NEXT_STEPS.md) is mirrored on the [task board](TASK_BOARD.md). Owner portal requirements, license selection and submission receipt remain unresolved.

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

Only the fixed owned fixture is accepted. Intake caps are 100 Python files, 256 KiB/file, 5 MiB total; a credential-free parser child has a 30-second deadline. These are process/input limits, **not an OS filesystem/network sandbox**. Hostile concurrent filesystem replacement is outside scope. No target code is executed, no runtime security is established, and no live source/model request has been made in this delivery. Explicit live transport is gated and disabled by default.

Joern is NOT_ATTEMPTED; LS-DATA-001 and LS-TRUST-001 are NOT_IMPLEMENTED. Local Git baseline `7797b85` exists on `feat/integrated-demo`; license selection is pending. The owner has authorized publication to the specified existing repository; see [document 23](docs/23_PORTABILITY_AND_RELEASE_VERIFICATION.md) for the actual outcome. Submission remains unverified. Generated scan reports are historical evidence; use new scan identities rather than editing old results.
