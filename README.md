<div align="center">

# Lazarus Sentinel

**Graph-first, evidence-backed application-security analysis.**
Correlate program structure with endpoints, permissions and trust boundaries, and get reproducible, human-reviewable findings. Defensive and read-only.

[![CI](https://github.com/sumitjadhav1703/Lazarus_Sentinel/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/sumitjadhav1703/Lazarus_Sentinel/actions/workflows/ci.yml)
![Python 3.13](https://img.shields.io/badge/python-3.13-3776AB?logo=python&logoColor=white)
![Node 24](https://img.shields.io/badge/node-24-339933?logo=nodedotjs&logoColor=white)
![Platforms](https://img.shields.io/badge/platforms-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)
![Status](https://img.shields.io/badge/status-controlled%20fixture-orange)

[Quickstart](#quickstart) · [How it works](#how-it-works) · [Roadmap](#roadmap) · [Contributing](#contributing) · [Docs](#documentation)

</div>

---

> **Honest scope.** The shipped release is a **controlled synthetic FastAPI fixture scanner**, not an arbitrary-repository security audit. A finding is a *candidate for human review*, never a confirmed vulnerability.

## Table of contents

- [What it is, and is not](#what-it-is-and-is-not)
- [Current status](#current-status)
- [Quickstart](#quickstart)
- [How it works](#how-it-works)
- [Using the CLI](#using-the-cli)
- [Viewer](#viewer)
- [Optional API credential](#optional-api-credential)
- [Quality checks](#quality-checks)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Documentation](#documentation)
- [Boundaries and safety](#boundaries-and-safety)
- [License](#license)

## What it is, and is not

| It is | It is not |
|---|---|
| Static, read-only analysis of owned, fixed fixtures | A scanner for arbitrary repositories or live sites |
| Deterministic, hash-linked evidence (file, lines, analyzer, rule) | An LLM guess: the model may explain evidence, never invent it |
| Explicit about `unknown`, `unresolved`, `unsupported` | A claim of a complete graph or of proven security |
| Severity, confidence and coverage kept separate | An exploit tool or auto-remediator |

## Current status

| Capability | Status |
|---|---|
| Intake | Fixed `fixture:fastapi-demo` identifier; manifest-bounded, read-only source parsing |
| Analysis | Python AST structure plus supported literal FastAPI routes/dependencies; no target imports or execution |
| Graph | Schema 0.1.0, deterministic identities, NetworkX MultiDiGraph, source hashes and locations |
| Rule | `LS-AUTH-001`: LOW-confidence declaration-gap candidates; opaque controls are diagnostics only |
| Persistence / report | SQLite committed references; graph, findings and coverage JSON; escaped Markdown |
| Measured demo | 6 endpoints, 23 nodes, 36 edges, 2 candidates, 3 matching declarations with effectiveness unverified |
| Quality | [Native Windows, macOS and Linux CI passed](docs/23_PORTABILITY_AND_RELEASE_VERIFICATION.md); 139 backend tests plus 1 Windows-only skip, 16 frontend tests at last verification |
| Demo | Hash-verified immutable bundle, disabled/mock explanation sidecars, fixed React + Cytoscape viewer; Meta adapter tested offline |
| Blocked / deferred | Live Meta access, Joern, data/trust rules, HTTP API, LangGraph, arbitrary repositories, OS isolation |

The fixture intentionally contains unsupported dynamic registration, so its normal outcome is **PARTIAL / exit 2**. A matching authorization declaration is syntax evidence, not proof of enforcement.

## Quickstart

Prerequisites: [Git](https://git-scm.com), [uv](https://docs.astral.sh/uv/), and Node.js 24 with npm. Python 3.13 is selected by `uv` from `.python-version`. No global packages or API keys are needed. Works the same in macOS/Linux terminals and Windows PowerShell.

```sh
git clone https://github.com/sumitjadhav1703/Lazarus_Sentinel.git
cd Lazarus_Sentinel
uv sync --project backend --locked
uv run --project backend --locked lazarus scan --target fixture:fastapi-demo
```

> **Exit code 2 is expected here.** 0 = completed with no relevant coverage gaps, 2 = useful partial output, 1 = failure. stdout is one JSON summary.

Artifacts land in `artifacts/scans/<scan_id>/{graph.json,findings.json,coverage.json,report.md}` and metadata in `artifacts/sentinel.sqlite3`. Repeated scans never overwrite each other. Evidence stores relative locations and hashes, not raw source excerpts.

Reproduce everything offline in one command:

```sh
npm ci --prefix frontend --ignore-scripts --no-audit --no-fund
uv run --project backend --locked python scripts/verify_demo.py
```

## How it works

```mermaid
flowchart LR
    A[fixture:fastapi-demo] --> B[Bounded snapshot<br/>intake.py]
    B --> C[Python AST adapter<br/>analysis.py / worker.py]
    C --> D[NetworkX graph<br/>models.py]
    D --> E[LS-AUTH-001<br/>rules.py]
    E --> F[(SQLite + JSON/Markdown reports<br/>persistence.py)]
    F --> G[Verified export bundle<br/>bundle.py]
    G --> H[React + Cytoscape viewer<br/>frontend/]
    F -.optional.-> I[Explanation sidecar<br/>disabled / mock / meta]
    I -.-> G
```

| Area | Files |
|---|---|
| CLI and coordination | `backend/src/lazarus_sentinel/cli.py`, `service.py` |
| Intake and extraction | `intake.py`, `worker.py`, `analysis.py` |
| Canonical facts | `models.py`, `rules.py` |
| Artifacts | `persistence.py`, `bundle.py`, `demo_models.py` |
| Explanation boundary | `explanations.py`, `meta_provider.py`, `budget.py` |
| Viewer | `frontend/src/`, fixed assets in `frontend/public/demo/v1/` |
| Reproduction | `scripts/verify_demo.py`, `prepare_demo.py`, `inspect_artifacts.py` |

Backend Pydantic schemas are authoritative. `CALLS` is not data flow; `DEPENDS_ON` is not enforcement. See [architecture](docs/02_ARCHITECTURE.md) and [graph schema](docs/03_GRAPH_SCHEMA.md).

## Using the CLI

```sh
uv run --project backend --locked lazarus --help
uv run --project backend --locked lazarus demo export --scan-id <SCAN_UUID>
uv run --project backend --locked lazarus explain --scan-id <SCAN_UUID> --finding-id <FINDING_ID>
uv run --project backend --locked lazarus explain --scan-id <SCAN_UUID> --finding-id <FINDING_ID> --provider mock
uv run --project backend --locked lazarus demo export --scan-id <SCAN_UUID> --annotation-id <ANNOTATION_UUID>
```

Substitute IDs returned by your own scan (finding IDs are in its `findings.json`). Explanation defaults to **DISABLED**. Mock output is offline, unreviewed assistance and never changes canonical findings. The Meta adapter needs explicit selection and reviewed access/privacy/budget gates; live verification is BLOCKED with zero paid calls, under a USD 3 / five-attempt cap and no retries.

## Viewer

```sh
npm ci --prefix frontend --ignore-scripts --no-audit --no-fund
npm run dev --prefix frontend
```

Open the loopback URL Vite prints. The viewer loads only the reviewed synthetic bundle in `frontend/public/demo/v1/`: search an endpoint, inspect a focused path, switch to the full graph, and select a node to see its source evidence. Fit/zoom/reset, keyboard step controls and expandable identity tables support deeper review. No upload, source path input or HTTP backend is involved. Details: [viewer design and verification](docs/20_VIEWER_CLARITY_AND_DESIGN.md).

The shipped dataset uses scan `d4788c12-b956-4535-b897-13744439093e` and bundle `f85376c4-9ec1-4b8f-aea2-1c0f89abae3e`, with a recorded mock annotation. Generated reports are historical evidence: create new scan identities instead of editing old ones.

## Optional API credential

Not needed for scans, the viewer or disabled/mock explanations. To prepare a local key file, copy [.env.example](.env.example) to `.env` once (`cp .env.example .env`, or `Copy-Item .env.example .env` in PowerShell) and fill in `MODEL_API_KEY`. `.env` is Git-ignored. The backend reads `MODEL_API_KEY`, not `META_API_KEY`, and the CLI does not load `.env` automatically: pass `uv run --env-file .env ...` when you choose to. Creating the file does not enable live calls. Keep credentials out of the frontend and all `VITE_*` variables.

## Quality checks

```sh
uv run --project backend --locked pytest backend/tests
uv run --project backend --locked ruff check backend/src backend/tests
uv run --project backend --locked ruff format --check backend/src backend/tests
uv run --project backend --locked mypy --config-file backend/pyproject.toml backend/src
npm --prefix frontend run typecheck && npm --prefix frontend run lint && npm --prefix frontend test
```

CI runs these as separate jobs on every pull request and on pushes to `main`, plus a 3-OS (macOS, Windows, Linux) offline verification and CodeQL. If a restricted environment cannot use the shared uv cache, see [document 21](docs/21_TEAM_HANDOFF.md).

## Roadmap

Planned work is tracked as [GitHub issues](https://github.com/sumitjadhav1703/Lazarus_Sentinel/issues) (labels `roadmap`, `good first issue`, `help wanted`). Gated plan: [next-phase plan](docs/22_NEXT_PHASE_PLAN.md) and [spec](spec/README.md).

- [ ] P03 fresh-clone reproduction on a second machine
- [ ] P04 accessibility feedback round
- [ ] P05 measure and, if justified, split the viewer chunk
- [ ] P07 one bounded, authorised live Meta explanation call
- [ ] P08 reviewed sandbox runtime with denial probes
- [ ] P09 bounded next-intake contract, optional Joern spike, `LS-DATA-001` / `LS-TRUST-001`
- [ ] P10 public demo on GitHub Pages
- [ ] S01 semantic contract for the next analysis stage

## Contributing

New here? Start with issues labelled [`good first issue`](https://github.com/sumitjadhav1703/Lazarus_Sentinel/labels/good%20first%20issue). Read [CONTRIBUTING.md](CONTRIBUTING.md) and the [team handoff](docs/21_TEAM_HANDOFF.md), branch from `main`, run `scripts/verify_demo.py`, and open a PR using the template. Report vulnerabilities privately per [SECURITY.md](SECURITY.md). Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Documentation

- Start: [team handoff](docs/21_TEAM_HANDOFF.md), [contributing](CONTRIBUTING.md), [task board](TASK_BOARD.md), [live log](AGENT.md), [platform evidence](docs/23_PORTABILITY_AND_RELEASE_VERIFICATION.md), [CI and issue backlog](docs/24_CONTRIBUTOR_READINESS_AND_CI.md).
- Contracts: [first slice](docs/13_FIRST_SLICE_CONTRACT.md), [demo delivery](docs/16_DEMO_DELIVERY_CONTRACT.md), [implementation review](docs/14_IMPLEMENTATION_REVIEW.md), [next steps](docs/15_NEXT_STEPS.md).
- Evidence: [capability report](docs/17_CAPABILITY_AND_RESEARCH_REPORT.md), [evaluation](docs/18_DEMO_EVALUATION.md), [integrated review](docs/19_INTEGRATED_DEMO_REVIEW.md).
- Reference: [00 Charter](docs/00_PROJECT_CHARTER.md), [01 Requirements](docs/01_REQUIREMENTS.md), [02 Architecture](docs/02_ARCHITECTURE.md), [03 Graph schema](docs/03_GRAPH_SCHEMA.md), [04 Rules](docs/04_ANALYSIS_RULES.md), [05 Orchestration](docs/05_ORCHESTRATION.md), [06 API/persistence](docs/06_API_AND_PERSISTENCE.md), [07 Frontend](docs/07_FRONTEND.md), [08 Security](docs/08_SECURITY_MODEL.md), [09 Evaluation](docs/09_TESTING_EVALUATION.md), [10 Roadmap](docs/10_IMPLEMENTATION_PLAN.md), [11 Decisions](docs/11_DECISIONS_AND_ASSUMPTIONS.md), [12 Sources](docs/12_SOURCES.md).
- Blueprint audit and next stage: [spec/](spec/README.md).
- AI-agent workflow (maintainers): [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md), [CODEX_BOOTSTRAP_PROMPT.md](CODEX_BOOTSTRAP_PROMPT.md).

## Boundaries and safety

Only the fixed owned fixture is accepted. Intake caps are 100 Python files, 256 KiB per file, 5 MiB total; a credential-free parser child has a 30-second deadline. These are process and input limits, **not an OS filesystem/network sandbox**. Hostile concurrent filesystem replacement is out of scope. No target code is executed, no runtime security is established, and no live source or model request has been made. Joern is NOT_ATTEMPTED; `LS-DATA-001` and `LS-TRUST-001` are NOT_IMPLEMENTED. Only analyse code you own or are authorised to assess.

## License

**Not yet chosen.** Publication to GitHub does not grant reuse rights. License selection is an open owner decision; see the license issue before reusing the code.
