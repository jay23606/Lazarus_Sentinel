# Contributing

Start with [team handoff](docs/21_TEAM_HANDOFF.md), [AGENTS.md](AGENTS.md), [current log](AGENT.md), [task board](TASK_BOARD.md) and [next phase](docs/22_NEXT_PHASE_PLAN.md). The current product analyzes one controlled synthetic fixture; contributions must preserve its evidence and coverage semantics.

Agree on a bounded task and file ownership with the coordinator, branch from the agreed integration baseline, and open a reviewable PR against the agreed integration branch. Do not force-push shared history. Inspect existing code and use its interfaces. Add focused regression checks for meaningful behavior changes, run `uv run --project backend --locked python scripts/verify_demo.py`, and report actual results and missing platform checks. Setup commands for macOS and PowerShell are in document 21; latest native/hosted outcomes are in [document 23](docs/23_PORTABILITY_AND_RELEASE_VERIFICATION.md).

Keep secrets, `.env` values, generated artifacts, local environments and the original blueprint PDF out of commits. Never execute target repositories or make model calls as part of ordinary checks. Preserve historical reports and use new identities. Critical/security decisions require owner-approved Astra or an explicit owner-approved fallback. Update affected documentation and coordinate AGENT.md/task-board updates before closing work.

Repository publication does not choose a license. License selection is pending owner decision; do not add a license or claim unrestricted reuse without that decision.
