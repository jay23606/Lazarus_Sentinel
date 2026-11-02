# Claude Code project entry point

@AGENTS.md
@docs/21_TEAM_HANDOFF.md

Read `AGENT.md`, `TASK_BOARD.md`, and the assigned task's contracts before changing code. `AGENT.md` is the living log; do not create a case-variant `Agent.md`.

Perform routine tasks only within the coordinator-assigned file boundary. Claude Code does not imply access to Codex Astra/Sol/Terra. Critical/security decisions require owner-approved Astra; if unavailable, stop that decision and request an approved fallback. Never fabricate model availability or silently substitute a Claude model for Astra.

Use the portable commands in document 21 and record measured checks, not historical counts. Preserve immutable artifacts, fixed synthetic scope and non-authoritative explanation wording. Do not read secret values, make paid calls, install global tools or widen intake.

These `@` imports follow [official Claude Code memory documentation](https://code.claude.com/docs/en/memory#import-additional-files), checked 2026-11-02. Verify loaded instructions with the installed client's supported context/memory inspection; model availability is separate from instruction loading.
