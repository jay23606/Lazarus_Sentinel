# 24 — Contributor readiness, CI and issue backlog

Written 2026-11-03 by Claude Code (Sonnet 5.5) for the owner. Read this so any agent (Codex or Claude) knows what changed in the repository's collaboration layer. It does not change product behaviour, fixtures, schemas, artifacts or the analyzer.

## What was done

1. **GitHub issue backlog.** 40 issues (#1–#40) were filed on `sumitjadhav1703/Lazarus_Sentinel`, with new labels `frontend`, `backend`, `testing`, `ci`, `security`, `roadmap`, `priority: high|medium|low`, `owner-decision`. Groups: #1–#10 docs/onboarding (good first issue), #11–#23 frontend (dark theme, accessibility, loading/error states, search, graph keyboard, component split, P10 GitHub Pages, P04 audit, P05 performance), #24–#28 testing (coverage, frontend unit tests, Playwright + axe, bundle secret-leak test, P03 fresh-clone), #29–#30 CI/security (CI hardening, Dependabot/CodeQL), #31–#39 roadmap (S01, N10 rules, Joern spike, P09, P08, P07, N17, N16), #40 LICENSE owner decision. Check live state with `gh issue list`; GitHub is the source of truth for status. Issues are plans, not completed work.
2. **CI rewritten** in `.github/workflows/ci.yml` (workflow name now `CI`, previously `Offline demo verification`). Triggers: `push` to `main` only, every `pull_request`, and `workflow_dispatch`. `concurrency` cancels superseded runs. Jobs: `backend` (ruff check, ruff format --check, strict mypy, pytest; Ubuntu), `frontend` (typecheck, lint, vitest, build, uploads `frontend-dist`; Ubuntu), and `verify` (needs both; macOS, Windows, Ubuntu matrix; runs `scripts/verify_demo.py` unchanged). Tool versions are pinned through workflow `env`: uv 0.12.5, Python 3.13.14, Node 24.14.0. Added `.github/workflows/codeql.yml` (Python and JS/TS; PR, push to main, weekly) and `.github/dependabot.yml` (Actions, uv in `/backend`, npm in `/frontend`).
3. **Community files:** `.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/{bug_report,feature_request,config}.yml` (blank issues off; security reports go to private advisories), `SECURITY.md`, `CODE_OF_CONDUCT.md`, a human-oriented `CONTRIBUTING.md`, and a rewritten `README.md` (badges, scope table, Mermaid architecture, quickstart, roadmap, doc map). Agent-routing text moved out of the README landing flow; `AGENTS.md`, `CLAUDE.md` and `AGENT.md` are unchanged in authority.
4. All of the above landed through PR #41 from branch `chore/contributor-ready`.

## Verification evidence (measured 2026-11-03)

- Local: `ruff check` passed; 139 backend tests passed, 1 skipped (Windows-only). Workflow and template YAML parsed with Ruby's YAML loader.
- PR #41 on GitHub: Backend, Frontend, Verify on Ubuntu and Windows, both CodeQL analyses passed. Verify on macOS was queued waiting for a hosted runner at the last check; record its final result before claiming macOS success for this commit.
- Earlier `main` push run 41494823283 (commit 9f3d021) showed **failure** only because the macOS job was *cancelled* before starting (Ubuntu and Windows jobs succeeded). That is a hosted-runner availability event, not a code defect; the jobs ran identical commands to the later passing run 41492178925 on 06f993e. Re-run the failed job instead of editing code if it recurs.

## Known limits and decisions left open

- **No LICENSE** was added; the owner must decide (issue #40). README says so explicitly.
- `actions/checkout@v7` and `actions/setup-node@v7`, `actions/upload-artifact@v4` and `github/codeql-action@v3` are tag-pinned, not SHA-pinned; only `setup-uv` is SHA-pinned. Tracked in the CI hardening issue.
- No coverage tool yet (issue #24). The README statement of 139 backend and 16 frontend tests is the last verified count, not a guarantee.
- Branch protection requiring the CI checks, private vulnerability reporting, and the repository Website field are owner actions in GitHub settings.
- Untouched on purpose: fixtures, immutable artifacts, packaged demo bundle, `.env`, the blueprint PDF, and the owner's other uncommitted documentation edits.

## Guidance for the next agent

Pick work from GitHub issues, keep one owner per file, branch from `main`, and run `uv run --project backend --locked python scripts/verify_demo.py`. Keep wording non-authoritative (candidate, not vulnerability). Critical/security decisions (for example the sandbox and intake issues) still require an owner-approved Astra or approved fallback. Append measured results to `AGENT.md`; do not create `Agent.md`.
