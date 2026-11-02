# 23 — Portability, team handoff and repository publication

Updated **2026-11-02**. This document owns the current macOS/Windows and GitHub publication evidence. Documents 14, 19 and 20 retain their historical verification results; the team setup and next phase are in [document 21](21_TEAM_HANDOFF.md) and [document 22](22_NEXT_PHASE_PLAN.md).

## Release scope

Publish reviewed source, synthetic fixtures/bundles, dependency locks, CI and maintained documentation to the owner's specified repository: [sumitjadhav1703/Lazarus_Sentinel](https://github.com/sumitjadhav1703/Lazarus_Sentinel). The repository was verified empty and public, and the connected account has push permission. Publication is authorized by the owner; no force push or deployment is required. The reviewed delivery is destined for `main`.

No environment, credential, local database, scan output, build output or dependency installation directory is included. The original blueprint PDF remains a local, unreviewed input and is not published. A project license is still an owner decision; public visibility is not a license grant or a hackathon submission receipt.

## Platform contract

Both systems use the same Python3.13.14 project lock, fixed fixture, graph schema and frontend lockfile. `.gitattributes` preserves LF text bytes across checkouts so source evidence and packaged assets do not drift through line-ending conversion.

| Boundary | macOS / POSIX | Windows |
|---|---|---|
| Source reads | Existing directory-relative/no-follow descriptor traversal | Exact-case bounded enumeration; reject all reparse-point components; bounded binary regular-file reads and pre/open/post identity checks |
| Portable names | Reject traversal/aliases and Windows-reserved names too | Reject device names, alternate streams, drive syntax, wildcard and trailing-dot/space aliases |
| Worker | Sanitized environment, input/output caps, wall-clock deadline and POSIX CPU/file-size/file-descriptor limits | Sanitized environment with required SystemRoot, input/output caps and parent wall-clock deadline; POSIX resource limits unavailable |
| Provider child | Existing fork path | Spawn path with importable offline test stubs; no production network in tests |
| Scan writer | POSIX advisory file lock | Windows byte-range lock; must preserve exclusion and release on process exit |
| Scripts | Portable uv/Python commands | Same commands; trusted fixed npm commands handle `.cmd` invocation |

Neither path establishes hostile-repository filesystem/network isolation. N14/N15 remain blocked. The Meta adapter stays disabled by default; no live calls or credentials are needed for setup, fixture scanning, viewer or tests.

## Verification and publication state

Native CI is configured for **macos-latest, windows-latest and ubuntu-latest** with fail-fast disabled so each platform reports independently. The full offline verifier checks backend tests, Ruff check/format, strict mypy, frontend type/lint/tests/build and shipped bundle integrity. Native Windows support is not verified merely by running a Windows branch under mocks on a Mac.

Local macOS verification: **138 backend tests passed, one native-Windows junction test skipped;16frontend tests passed; allnineoffline checks passed.** Strict mypy for default,win32,darwin andlinux platforms passes16sourcefiles each. Final independent Astra review accepted the bounded runtime/static-guard changes after review findings were repaired. These results do not substitute for native Windows execution.

At this preparation checkpoint, remote publication and native CI are pending. Exact release commit, remote identity and native job URLs will be recorded below after they are observed.

## Teammate operating instructions

Use the exact clone/setup commands in document21. `AGENTS.md` carries shared constraints, `CLAUDE.md` imports them for Claude Code, and `AGENT.md` is the canonical state and append-only log. Do not add `Agent.md` alongside it: those names collide on common macOS/Windows filesystems. Branch from current remote `main`; assign one file owner per task and use PRs with platform checks.

Only `fixture:fastapi-demo` is accepted. A normal scan is intentionally PARTIAL/exit2: six endpoints,23nodes,36edges,twoLOW-confidence candidates and three matching declarations with effectiveness unverified. These outcomes are synthetic declaration-context evidence, not runtime authorization or data-flow proof. Keep stored bundle/source identities unchanged unless intentionally creating new evidence.
