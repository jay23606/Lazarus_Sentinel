# Contributing

Thanks for helping. This project is a defensive, read-only analyzer that currently handles one controlled synthetic fixture. Contributions must preserve its evidence and coverage semantics.

## Find something to work on

Pick an issue labelled [`good first issue`](https://github.com/sumitjadhav1703/Lazarus_Sentinel/labels/good%20first%20issue), or one tagged `frontend`, `testing`, `ci` or `documentation`. Comment to claim it so two people do not edit the same files. Larger items are tagged `roadmap` or `help wanted`.

## Set up

Prerequisites: Git, [uv](https://docs.astral.sh/uv/), Node.js 24 + npm.

```sh
git clone https://github.com/sumitjadhav1703/Lazarus_Sentinel.git
cd Lazarus_Sentinel
uv sync --project backend --locked
npm ci --prefix frontend --ignore-scripts --no-audit --no-fund
uv run --project backend --locked python scripts/verify_demo.py
```

See [docs/21_TEAM_HANDOFF.md](docs/21_TEAM_HANDOFF.md) for module ownership and Windows/macOS notes.

## Workflow

1. Branch from current `main`: `git switch -c feat/<short-task>` (or `codex/<short-task>` for agent work).
2. Make the smallest complete change; inspect existing code and tests first.
3. Add focused tests for behaviour changes.
4. Run the checks (backend: `pytest`, `ruff check`, `ruff format --check`, `mypy`; frontend: `npm run typecheck`, `lint`, `test`, `build`) or the full `scripts/verify_demo.py`.
5. Open a PR with the template. Describe behaviour, evidence and limits. Require one human review and green CI before merge. Do not force-push shared history.

## Non-negotiables

- Read-only and defensive: never execute target repositories, never generate exploits, no network scanning, no widening intake beyond the fixed fixture without a reviewed contract.
- Wording: a finding is a **candidate**. Keep `severity`, `confidence` and `coverage` separate, and keep `unknown` explicit.
- No secrets: never commit `.env` values, credentials, local environments, generated artifacts or the blueprint PDF. No model or paid calls in ordinary checks.
- Preserve historical reports and packaged evidence; create new identities instead of rewriting.
- Update affected docs. Architectural decisions go in `docs/11_DECISIONS_AND_ASSUMPTIONS.md`.

## Maintainers and AI agents

The agent workflow (`AGENTS.md`, `CLAUDE.md`, `AGENT.md`, `TASK_BOARD.md`) applies to coordinated agent work: coordinator assigns file ownership, critical/security decisions need an owner-approved reviewer or fallback, and `AGENT.md` is the canonical living log (never create `Agent.md`).

## License

Not yet chosen (owner decision, tracked in an issue). Do not add a license file or claim unrestricted reuse until decided.
