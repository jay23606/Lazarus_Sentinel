# 22 — Next phase: finite, gated team plan

Proposed execution order, updated 2026-11-02. Completed baseline/demo/viewer work must not restart. [Document 15](15_NEXT_STEPS.md) preserves N01–N18 dispositions; this plan turns remaining work into finite team assignments. [Document 23](23_PORTABILITY_AND_RELEASE_VERIFICATION.md) records actual current checks and publication outcomes. A listed action is not evidence of execution.

| ID | Owner / dependency | Bounded task and acceptance gate |
|---|---|---|
| P01 | Coordinator + backend; first | Finish native Windows/macOS compatibility without weakening worker isolation, provider deadline, redaction or budget concurrency. Run locked offline verifier on native macOS and hosted Windows/macOS/Linux. Record exact commit, runner, counts and links; unsupported isolation stays explicit. |
| P02 | Coordinator; P01 checks | Publish the reviewed source to the owner-specified existing repository and branch; inspect existing remote history first, never force-push. Verify remote branch identity and hosted CI. Preserve owner PDF, secrets and generated evidence locally. License and default-branch choices remain explicit. |
| P03 | Teammate + coordinator; P02 | Reproduce from a fresh clone on a second machine with document 21. Verify expected PARTIAL scan and fixed viewer without credentials. Return platform/tool versions, all checks, one screenshot and exact blockers. Close only with recorded results; fix instructions rather than resetting old evidence. |
| P04 | UI teammate; independent of owner portals | Conduct one bounded feedback round across first-time users, developers and security reviewers. Test native 200% browser zoom and a real screen reader, keyboard selection, focus, 320px reflow, declaration/unknown wording and error states. Record browser/AT versions and observed issues; triage before any redesign. |
| P05 | UI teammate; measured need | Measure production cold load and graph render on the fixed 23-node graph. Existing roughly 839 kB chunk warning is not a benchmark. Consider lazy loading/code splitting only if measured latency or payload cost justifies it; preserve hash validation and accessible fallback. No arbitrary large-graph program in this task. |
| P06 | Owner; can run alongside P01–P05 | Resolve N01/N02/N13: portal eligibility, complete required deliverables, privacy/data-use mode, Meta account/model access and license. Do not reveal credentials. Record primary-source dates and owner decisions. No submission or paid request is implied. |
| P07 | Backend + Astra; P06 prerequisites | Only after explicit live-call authorization, recheck exact Meta protocol/model/prices and existing USD3/five-attempt shared ledger. Run one bounded synthetic explanation, no retry; retain immutable identities, usage/provenance and validated citations. Failed/ambiguous usage blocks further calls pending reconciliation. A successful call proves transport only, not security accuracy. |
| P08 | Security/Astra + infrastructure; before N15 | Resolve N14 with a reviewed runtime. Prove filesystem/network/credential denial, resource/deadline limits, cleanup and no host socket/agent exposure using controlled probes. A process limit or Windows Job Object is not filesystem/network sandbox evidence. Owner approves platform/runner before installation. Broader intake stays blocked until measured review passes. |
| P09 | Backend + research/Astra; P08 | Freeze one explicitly authorized, bounded next intake contract with provenance, caps, threat model, unknowns and predeclared fixture oracle. Implement only that contract. Joern spike remains optional/time-bounded; DATA/TRUST require real data-flow/policy evidence, never relabel CALLS. |

## Step-by-step execution rule

1. Coordinator selects one ready task, names its owner/files and freezes acceptance criteria. P06 owner work and P04 research can proceed independently.
2. Read current implementation and evidence; identify affected callers/tests/fixtures/config. Preserve backend-generated schema authority.
3. Make a scoped branch and smallest change. Use independent agents only within non-overlapping ownership boundaries.
4. Run relevant tests and integration checks; obtain Astra review for security-sensitive changes. Record unavailable checks as BLOCKED or NOT_RUN.
5. Update task board, decision register when necessary, and append AGENT.md session evidence. Close the P-item only after its acceptance gate is observed.

Keep the demo working throughout. No speculative API, LangGraph, microservices, upload UI, automatic remediation or global tool installation is required by this plan. A broader accuracy program, retention service and multi-language scanner remain separate future proposals.
