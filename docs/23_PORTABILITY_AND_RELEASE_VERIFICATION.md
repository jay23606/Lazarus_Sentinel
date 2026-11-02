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

Publication verified: [commit28798be](https://github.com/sumitjadhav1703/Lazarus_Sentinel/commit/28798bef8a36f8b0949bea7f36d193a6f8acf361) is on remote `main`, with full reviewed history and the CI workflow. The first HTTPS/OAuth push was refused because that credential lacked workflow scope; nothing was published by that attempt. The existing SSH connection authenticated as the repository owner and published the complete branch without changing OAuth scopes or dropping CI.

Native verification run: [Offline demo verification](https://github.com/sumitjadhav1703/Lazarus_Sentinel/actions/runs/41491302001). Final native outcomes will be recorded after the jobs finish.

## Teammate operating instructions

Use the exact clone/setup commands in document21. `AGENTS.md` carries shared constraints, `CLAUDE.md` imports them for Claude Code, and `AGENT.md` is the canonical state and append-only log. Do not add `Agent.md` alongside it: those names collide on common macOS/Windows filesystems. Branch from current remote `main`; assign one file owner per task and use PRs with platform checks.

Only `fixture:fastapi-demo` is accepted. A normal scan is intentionally PARTIAL/exit2: six endpoints,23nodes,36edges,twoLOW-confidence candidates and three matching declarations with effectiveness unverified. These outcomes are synthetic declaration-context evidence, not runtime authorization or data-flow proof. Keep stored bundle/source identities unchanged unless intentionally creating new evidence.


### Initial native result and canonical-path repair

The first native run passed allninechecks onUbuntu. Windows passed eight gates but failed backend tests (18failed/121passed):17artifact/export/inspection checks exposed backslash serialization in stored references, and one router test constructed noncanonical snapshot paths. Production intake already required POSIX snapshot names. The repair serializes artifact/summary paths with `.as_posix()` and fixes both test snapshot producers; strict bundle/inspector validation and route analysis remain unchanged. A PureWindowsPath regression failed before the repair and passed afterward.

Fresh local verification after this repair: **139 backend passed, one Windows-only skip;16frontend passed;allnineoffline gates and strict win32/darwin/linux mypy passed.** Astra accepted the narrow repair read-only. A new commit/run will verify Windows again; the initial failed result is preserved rather than silently rerun. Native macOS job was still queued at this observation.


### Verified release — all native jobs passed

The corrected source commit [06f993e](https://github.com/sumitjadhav1703/Lazarus_Sentinel/commit/06f993e77237086ecf0f2abb40670082b6c84be0) is published on `main`. [Native CI run41492178925](https://github.com/sumitjadhav1703/Lazarus_Sentinel/actions/runs/41492178925) completed **SUCCESS** on2026-11-02. All jobs performed clean locked setup and allnineoffline verifier gates:

| Native runner | Observed result | Job evidence |
|---|---|---|
| Windows | PASS | [Windows job](https://github.com/sumitjadhav1703/Lazarus_Sentinel/actions/runs/41492178925/job/125437729293) |
| macOS | PASS | [macOS job](https://github.com/sumitjadhav1703/Lazarus_Sentinel/actions/runs/41492178925/job/125437729874) |
| Ubuntu/Linux | PASS | [Linux job](https://github.com/sumitjadhav1703/Lazarus_Sentinel/actions/runs/41492178925/job/125437730148) |

This verifies the bounded fixture/backend workflow and frontend installation, tests and production build on each native runner. Local Mac counts are139backend passed/oneWindows-only skip and16frontend tests. Windows-specific tests run on the Windows job; no broad skip was used to conceal the original failures. Hosted results are per-job gates rather than an invented universal test-count total.

The initial run is superseded; its Windows failure and diagnosis remain documented above. The previously queued obsolete run was canceled after the corrected run passed, rather than consuming more runner time. No failed provider/model call was retried; no live provider call occurred. Final documentation may have a later commit than the source commit linked here; it does not change the tested source.

**Completed:** P01 bounded native portability and P02 publication/verification. **Next:** P03 teammate fresh-clone reproduction, P04 accessibility/user feedback, P05 measured loading/rendering, and owner P06 account/event/license decisions. P07liveverification and P08isolation/P09intake remain separately gated. No installer, hostile-repository isolation, live Meta access, portal submission or license grant is claimed.
