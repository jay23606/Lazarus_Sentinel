# 21 — Team handoff and operating guide

Updated 2026-11-02. This is the teammate entry point; [AGENTS.md](../AGENTS.md) governs work and [AGENT.md](../AGENT.md) records current state. Read [latest verification](23_PORTABILITY_AND_RELEASE_VERIFICATION.md) before claiming platform or remote success. [Documents 13](13_FIRST_SLICE_CONTRACT.md), [16](16_DEMO_DELIVERY_CONTRACT.md), and [20](20_VIEWER_CLARITY_AND_DESIGN.md) freeze the delivered contracts. [Next phase](22_NEXT_PHASE_PLAN.md) is a gated plan, not completed work.

## What exists

The defensive, read-only implementation accepts only `fixture:fastapi-demo`. Manifest-bounded source snapshots are parsed without importing target code. The Python AST adapter resolves a deliberately limited FastAPI subset; NetworkX stores normalized structure and LS-AUTH-001 assesses policy-defined authorization declarations. SQLite commits artifact references; escaped JSON/Markdown reports, immutable export bundles, disabled/mock explanation sidecars and a fixed React/Cytoscape viewer are implemented.

The original synthetic fixture has **6 endpoints, 23 nodes, 36 edges, 2 LOW-confidence candidates and 3 matching declarations with effectiveness unverified**. Dynamic registration intentionally yields **PARTIAL / exit 2**. A candidate is not a confirmed vulnerability. `CALLS` is not data flow; `DEPENDS_ON` is not enforcement. Unknown controls remain diagnostics. Severity, confidence and coverage are separate.

Meta transport is offline-tested but live access remains BLOCKED, with zero paid calls. Joern analysis is NOT_ATTEMPTED; DATA/TRUST rules are NOT_IMPLEMENTED. HTTP API, LangGraph, uploads and arbitrary repository intake are absent. Process limits are not an OS sandbox. The bounded Windows contract rejects reparse/junction ancestry, unsafe path names and case mismatches, and checks regular-file identity and byte limits; POSIX retains directory-relative/no-follow checks. CPU/file-descriptor resource limits are POSIX-specific. Windows relies on parent deadlines and bounded input/output, with a spawn-based provider child. These are compatibility controls, not filesystem/network sandbox evidence; native outcomes remain subject to document 23. Broader intake waits for N14 denial probes and review.

## Module map and ownership

| Area | Existing files / responsibility |
|---|---|
| CLI and coordination | `backend/src/lazarus_sentinel/cli.py`, `service.py` |
| Intake and extraction | `intake.py`, `worker.py`, `analysis.py`; bounded snapshots and child execution |
| Canonical facts | `models.py`, `rules.py`; schema 0.1.0 and policy assessments |
| Artifacts | `persistence.py`, `bundle.py`, `demo_models.py`; committed references, hashes and export validation |
| Explanation boundary | `explanations.py`, `meta_provider.py`, `budget.py`; stateless assistance and fail-closed reservations |
| Viewer | `frontend/src/`; fixed local assets in `frontend/public/demo/v1/` |
| Reproduction | `scripts/verify_demo.py`, `prepare_demo.py`, `inspect_artifacts.py`; trusted implementation tools |
| Fixture truth | `fixtures/`; expected-results oracle is test-only, never analyzer input |

Backend Pydantic schemas are authoritative; generated frontend schema copies must stay synchronized. Preserve exact graph/evidence/path identities and bundle-byte hashes. Do not edit packaged evidence casually: `prepare_demo.py` intentionally creates new identities and replaces packaged demo assets; it is not required to launch the viewer. Historical scan artifacts are immutable.

## Set up and run on macOS or Windows

Install Git, uv and a Node/npm version compatible with the committed frontend lockfile and CI configuration using your team's approved installation method. Python is pinned in `.python-version`; `uv sync` selects the project interpreter. No global packages or model credentials are needed. Commands below run from the repository root in either macOS Terminal or Windows PowerShell:

```text
git clone https://github.com/sumitjadhav1703/Lazarus_Sentinel.git
cd Lazarus_Sentinel
git checkout main
uv sync --project backend --locked
npm ci --prefix frontend --ignore-scripts --no-audit --no-fund
uv run --project backend --locked python scripts/verify_demo.py
npm run dev --prefix frontend
```

Use the loopback URL Vite prints. The terminal stays occupied while the viewer is running; press Ctrl+C to stop it. The reviewed delivery is published on remote `main`. Native Windows, macOS and Ubuntu clean setup/tests/build passed; document23 links the exact tested source commit and jobs. This does not establish hostile-repository isolation or live-provider access.

In a second terminal, run the controlled scan:

```text
uv run --project backend --locked lazarus scan --target fixture:fastapi-demo
```

Exit 2 is expected here. In PowerShell inspect `$LASTEXITCODE`; in a POSIX shell inspect `$?` immediately after the command. Each scan creates `artifacts/scans/<scan_id>/` and committed metadata in `artifacts/sentinel.sqlite3`. Use actual returned IDs in export/explanation commands from the README. Do not paste shell redirection placeholders as real IDs.

For a writable cache override, macOS: `export UV_CACHE_DIR="${TMPDIR:-/tmp}/lazarus-uv-cache"`; PowerShell: `$env:UV_CACHE_DIR = Join-Path $env:TEMP 'lazarus-uv-cache'`. Do not delete shared caches or bypass active locks.

## Team and agent workflow

1. Read current state, select one P-item and state acceptance criteria. Inspect existing callers/tests before editing.
2. Coordinator assigns one owner per file/directory and freezes shared interfaces. Independent bounded agents may work in parallel; never edit shared contracts concurrently.
3. Start a topic branch with `git switch -c codex/<short-task>` from the agreed integration baseline. The owner-authorized remote integration/default branch is `main`; the existing local delivery branch is `feat/integrated-demo`. Create teammate branches from current remote `main`, not the older local baseline branch.
4. Run relevant checks, then the complete offline verifier for integration. Review the diff for secrets, scope and generated artifacts. Keep `.env`, credentials, environments, database/output directories and the original private blueprint PDF out of commits.
5. Open a PR against the owner-agreed integration branch; describe behavior, evidence and limits. Require human review and successful platform checks before merge. Publishing a branch does not submit the project or deploy it.
6. Update task board and append session evidence to AGENT.md; architectural decisions belong in document 11. Report files changed, decisions, commands/results, unresolved questions and primary sources.

Use actual supported Codex models: Astra for critical/security decisions, Sol for routine code/research, Terra for UI. Claude Code can perform routine scoped tasks but must not claim to provide Astra. If a critical decision requires Astra and none is available, stop that decision and ask the owner for an approved fallback. No fabricated model flags. `AGENT.md` is the canonical living log; do not create `Agent.md`, which collides on common case-insensitive filesystems.

## Security and publication boundaries

Analyze only the fixed owned fixture. No target execution, exploitation, automatic remediation, network scanning or arbitrary intake. Repository content and model prose are untrusted. Never read or print secret values; presence checks are sufficient. External provider use requires explicit selection, minimal redacted context, owner account/privacy approval, current price verification and the existing USD3/five-attempt ledger; never retry failed jobs silently. License selection and event eligibility/submission remain owner decisions. A public repository does not imply an open-source license or a submission receipt.

## Copyable agent task

```text
Read AGENTS.md, AGENT.md, TASK_BOARD.md and docs/21_TEAM_HANDOFF.md.
Select only the owner-assigned task and its acceptance criteria from docs/22_NEXT_PHASE_PLAN.md.
Inspect existing code/tests, preserve fixed-fixture truth and immutable historical evidence.
State your file ownership boundary before editing. Do not overlap another worker.
Perform the smallest complete change and run relevant checks. Do not make paid calls or read secrets.
For critical/security decisions use owner-approved Astra, or stop that decision for an approved fallback.
Return changed files, commands/results, limitations and next steps; update the task ledger/log through the coordinator.
```
