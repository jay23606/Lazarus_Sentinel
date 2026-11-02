# 15 — Complete next-step checklist

Updated **2026-11-02**. This is the recommended roadmap after the completed first slice, not authorization to implement every item. Document 13 remains the approved implemented scope; document 14 contains verification evidence. Task IDs below are mirrored in TASK_BOARD.md.

## Integrated demo status — 2026-11-02

The approved [demo contract](16_DEMO_DELIVERY_CONTRACT.md) is implemented alongside the preserved first-slice analyzer: immutable hash-verified bundles, disabled/mock explanations with a gated Meta adapter, and a fixed React/Vite/TypeScript/Cytoscape viewer. See [capability gates](17_CAPABILITY_AND_RESEARCH_REPORT.md), [finite evaluation](18_DEMO_EVALUATION.md), and [integrated verification](19_INTEGRATED_DEMO_REVIEW.md) for current checks and review disposition. Document 14 remains historical first-slice evidence; its 73-test count is not the integrated total.

Local baseline commit `7797b85` is preserved on `feat/integrated-demo`; no remote, publication, submission or license selection is implied. Only fixed synthetic intake is supported. Live access is BLOCKED by the missing key; zero paid calls were made. Joern setup is blocked and analysis NOT_ATTEMPTED; data/trust rules remain NOT_IMPLEMENTED. OS sandbox launch failed before execution, so broader intake remains blocked.

## Current disposition of every task

| ID | Status | Evidence / remaining gate |
|---|---|---|
| N01 | BLOCKED | Owner portal acceptance, complete rules and receipt unknown. |
| N02 | BLOCKED | Missing key/account verification; no live request. |
| N03 | DONE; license pending | Local baseline 7797b85 and feat/integrated-demo; no remote/publication. |
| N04 | DONE | Predeclared variant: 3 endpoints, 1 candidate, 1 declaration, 1 unknown; finite synthetic evaluation only. |
| N05 | DONE | Bundle/explanation/viewer contract frozen in document 16. |
| N06 | DONE | Fixed accessible graph/findings/coverage viewer; final checks/review in document 19. |
| N07 | DONE | Disabled/offline mock boundary and hostile-output validation; canonical facts unchanged. |
| N08 | ADAPTER TESTED; live BLOCKED | Explicit Meta adapter and transactional budget; zero paid calls; USD3 / five-attempt cap. |
| N09 | SETUP_BLOCKED; NOT_ATTEMPTED | Joern v4.0.666 pinned; release README JDK21 versus installation docs19; installed JDK26. No Joern; 1.64GB asset not downloaded. |
| N10 | NOT_IMPLEMENTED | DATA/TRUST capability/policy gates unmet; CALLS is not value flow. |
| N11 | SKIPPED | Fixed assets meet demo need; no HTTP service. |
| N12 | DONE (offline) | Exact integrated checks and Astra disposition are authoritative in document 19. |
| N13 | LOCAL MATERIALS READY; submission BLOCKED | Synthetic bundle and local walkthrough available; portal requirements/receipt unknown. |
| N14 | BLOCKED | sandbox-exec exit71: sandbox_apply: Operation not permitted. Denial probes not run; no enforced isolation claim. |
| N15 | BLOCKED | Requires N14 before broader authorized intake. |
| N16 | FINITE PILOT DONE; broader OPEN | Controlled variant support measured; no broad accuracy or interprocedural/data-flow claim. |
| N17 | FINITE TRANCHE DONE; broader OPEN | Read-only inspector, scripts and credential-free CI configuration present; hosted CI NOT_RUN; clean-copy verification passed in document 19. Retention/triage/remote service remain open. |
| N18 | FINITE RESEARCH DONE; broader OPEN | Catalog and DATA/TRUST research in document 17; broad detector/language program remains future work. |

The detailed exit criteria below remain useful for unresolved portions; completed work must not be restarted. Status above supersedes prospective wording below.

## Step-by-step sequence

### N01 — Confirm event participation and submission requirements

- **Owner:** project owner. **Dependency:** none; do this first.
- Confirm acceptance, track/team membership, official rules, required Meta technology use, allowed pre-existing work, repository visibility/license requirements, submission fields, video requirements, and account access in the actual organizer portal.
- The [public event page](https://dev.meta.ai/events/global-hackathon), reopened 2026-11-02, still lists **November 4, 2026, 9:00 PM ET = November 5, 2026, 7:30 AM IST**. Dates can change. Public event information does not establish this owner's acceptance or the complete submission rules.
- **Done when:** organizer requirements/deadline are recorded with evidence; unknown or unavailable requirements are explicitly blocked. Do not claim the present offline slice is submission-ready.

### N02 — Check runtime Meta access before building its adapter

- **Owner:** owner for access; Sol for source verification; Astra for privacy/security review. **Dependency:** N01 requirements; access check can run alongside N03–N05.
- Confirm credential configuration without displaying values, account/model permissions, region eligibility, quota/billing, approved spend, and applicable data-use mode. No secret should be pasted into docs or reports.
- Current [official overview](https://dev.meta.ai/docs/overview) documents `https://api.meta.ai/v1`, `MODEL_API_KEY`, and Standard Muse Spark model IDs. Confirm the exact selected model/request contract again before implementation; documentation availability is not account access.
- For later authorized verification, send one minimal synthetic request with bounded tokens/time/cost and retain redacted metadata/error, not a key or full prompt log. This documentation update makes no request.
- Use Standard mode for the proposed integration. [Standard mode excludes training use; Contributor mode allows submitted content to train models](https://dev.meta.ai/docs/pricing-rate-limits). Standard mode is not a zero-retention promise.
- **Done when:** an authorized synthetic request succeeds under the reviewed mode, or the access failure is recorded and the product continues offline. Reconcile event requirements rather than calling a mock eligible by assumption.

### N03 — Preserve a versioned local baseline

- **Owner:** owner/coordinator; Sol for repository setup. **Dependency:** none.
- Initialize a local Git repository as a separately selected execution task; review ignores, source/fixture files, lockfile, docs, and absence of credentials/generated artifacts before the first commit. Decide project license and dependency notices with the owner.
- Keep `.venv`, caches, `.env`, and scan artifacts out of commits. Do not push/publish without explicit instruction; a remote repository is not required for local reproducibility.
- Continue using the scanned-byte manifest for source evidence; a Git commit supplements it and never substitutes for dirty/untracked content identity.
- **Done when:** a reviewed baseline commit can be reproduced locally, or a dated source archive/content inventory is retained pending Git setup. Baseline 7797b85 now exists; license remains owner-selected and pending.

### N04 — Lock the demo and evaluation fixture

- **Owner:** Sol; Astra reviews security meaning. **Dependency:** current baseline.
- Manually review weak, authentication-only, declared-authorization, public/no-policy, and unsupported cases. Keep policy assertions separate from the expected-results oracle.
- Preserve the current 73-test baseline and exact endpoint/candidate/declaration expectations. Add a second controlled synthetic fixture or variants with predeclared expected paths before claiming broader extraction/rule coverage.
- Record candidate counts, unsupported cases, path/evidence correctness, repeat determinism and measured elapsed time. Separate unknown diagnostics from seeded weakness detections; a recognized declaration is not a runtime-safe label.
- **Done when:** evaluation scenarios/expected outputs are versioned, every displayed candidate is manually traceable, and baseline results are reproducible. Do not claim production detection accuracy from this small corpus.

### N05 — Freeze the next demo interfaces and cut line

- **Owner:** coordinator + Astra; Sol/Terra consume the contract. **Dependency:** N04; provider requirements informed by N01/N02.
- Keep graph schema 0.1.0 and existing finding/evidence IDs. Freeze the artifact-loader, selected-path, coverage-display and explanation request/response examples before parallel work.
- **Default:** fixed, validated synthetic artifact dataset → local viewer. An HTTP API, scan-start UI, file uploads, arbitrary path input and remote deployment are not prerequisites.
- Decide which artifacts can be bundled; retain schema/version/hash checks and source minimization. Display errors/unknowns when artifacts are invalid rather than a success-shaped empty graph.
- **Done when:** one written next-increment contract and example dataset define what frontend and explanation work can consume. The selected demo increment is now implemented under document 16; remaining expansion is separately gated.

### N06 — Build the minimum graph/findings/coverage viewer

- **Owner:** Terra for UI; Sol for data loading; Astra reviews security claims. **Dependency:** N05.
- Prefer React/Vite/TypeScript with Cytoscape.js from the existing frontend specification, subject to project-local dependency compatibility. Load the fixed synthetic artifacts; do not rebuild the analyzer in JavaScript.
- Show repository revision/status, graph counts, findings, LOW confidence separately from severity, source locations/hashes, and unknown coverage. Select a finding to highlight its exact ordered path; show why each edge exists.
- Provide a table/list fallback, keyboard selection, accessible non-color status labels, invalid-data states, and an element/render cap. Show dependency declarations with effectiveness unverified.
- **Done when:** the six supported endpoints, two candidate paths, declared-control comparison and unsupported route case can all be inspected. No invented graph facts or generic chatbot screen.
- **Cut option:** if UI integration threatens the freeze, retain the verified Markdown/JSON walkthrough and a bounded static graph view; do not add an HTTP service just to complete a stack diagram.

### N07 — Add an offline explanation boundary and hostile-output tests

- **Owner:** Sol; Astra approves guardrails. **Dependency:** N05; can run alongside N06.
- Define a replaceable provider interface and deterministic mock using only selected existing evidence, graph paths, unknowns and approved minimal metadata. Do not send whole repositories.
- Keep explanations separate, visibly model-assisted and non-authoritative. They cannot change graph facts, findings, severity/confidence or confirmation status.
- Validate response schema and evidence-ID allowlist. Test invented IDs, malformed output, prompt-injection strings, timeout/provider failure and attempted status/fact changes. Schema-valid prose still needs factuality review.
- **Done when:** offline explanations are testable and optional; invalid output is rejected and static results remain available.

### N08 — Integrate live Meta explanations only after access/privacy gates

- **Owner:** Sol implements; Astra reviews; owner supplies authorized access/spend. **Dependencies:** N02 + N07.
- Pin the actual documented API/model contract and approved Standard mode. Enforce minimal synthetic-only context initially, redaction/egress disclosure, token/time/spend bounds and safe error handling.
- Keep default disabled; key presence does not enable calls. Preserve disabled/mock mode and leave deterministic analysis unchanged when the provider fails.
- Manually review the exact demo explanation: evidence-ID checks cannot prove its prose is factual. Label cached recordings separately from live responses and never pass mock output off as live.
- **Done when:** one selected real finding receives a useful bounded explanation with zero accepted invented references/claims in the reviewed demo, and offline/failure paths pass. If blocked, record the blocker and reassess submission requirements; do not invent API success.

### N09 — Consider a measured analyzer capability spike (optional before demo freeze)

- **Owner:** Sol compatibility researcher; Astra adjudicates capabilities. **Dependency:** N04; separate local installation authorization/necessity review if tools are absent.
- Timebox setup and measurement to **two hours total** as a proposed cap. Verify platform/runtime/license and installed CLI help. Use a pinned tool/version and controlled fixture only; retain commands, raw redacted errors, graph samples, elapsed time and resources if measured.
- Compare known function/call/source mappings, same-function and cross-function flow positives with safe controls, explicit unresolved constructs and repeatability. Joern has Python support; neither docs nor parsing success proves useful FastAPI/data-flow semantics.
- **Done when:** a written per-capability go/no-go matrix exists. If blocked or timebox exceeded, preserve NOT_ATTEMPTED/FAILED distinctions and keep AST structure analysis. Never convert CALLS to FLOWS_TO or build a substitute taint compiler to satisfy a checklist.

### N10 — Gate LS-DATA-001 and LS-TRUST-001 separately

- **Owner:** Astra for policy/semantics; Sol implements only a frozen supported subset. **Dependency:** N09 measured capabilities or another explicitly reviewed analyzer; not a precondition for the current demo.
- LS-DATA-001 requires demonstrated source, value propagation, sink, handling-control semantics and exact path evidence. Call reachability alone fails this gate.
- LS-TRUST-001 requires an explicit boundary/expected-handling policy and evidence for the transition; crossing a boundary alone is not a vulnerability.
- For each family: define positive, safe and unknown scenarios; version policy/rule; validate every path; report severity/confidence/coverage separately; rerun Astra review. Do not report an unknown control as absent.
- **Done when:** that individual rule passes its capability/evaluation gates. Otherwise retain NOT_IMPLEMENTED/UNSUPPORTED and explain it. These two families are independent future tasks, not three working detectors promised for submission.

### N11 — Add a local API only if the chosen demo actually needs one

- **Owner:** Sol; Astra approves exposure and file-access boundary. **Dependency:** N05/N06 product need.
- Freeze minimal read-only scan/artifact/graph/finding/coverage/error examples from document 06. Read only validated committed artifact references, not arbitrary client paths. Decide local binding, access/origin policy, graph pagination/neighborhood limits and tamper/error behavior before coding.
- Add scan-start/triage writes separately only when requested; preserve fixture allowlist. Remote multi-user authentication, tenancy and uploads are separate products/security gates.
- **Done when:** the selected local view works through contract tests without broad filesystem/network exposure. Skip this step if fixed artifact loading meets the demo need.

### N12 — Run the integrated evaluation and security review

- **Owner:** Sol QA + Terra UI verification + independent read-only Astra. **Dependencies:** chosen N06–N08 demo work; N09–N11 only if included.
- Run Python quality checks, new frontend checks/build, offline end-to-end path selection, malformed/tampered artifacts, provider disabled/mock/failure cases, and live synthetic verification only if authorized.
- Confirm candidate/declared-control/unknown examples, stable IDs, source/artifact hashes, escaped labels, no raw credentials/private-source egress, and separate severity/confidence/coverage.
- **Done when:** no material review issue remains; exact tool/version/fixture/test outcomes and remaining limitations are recorded. Passing tests is not proof of security efficacy or arbitrary-repository isolation.

### N13 — Freeze, record, and submit the scoped demo

- **Owner:** owner + coordinator; Terra for presentation; Sol for reproducibility. **Dependencies:** N01 and N12, plus actual required provider use under organizer rules.
- Prepare clean-checkout setup, dependency/license notices, architecture/supported-pattern description, evaluation numbers with denominators, limitations, screenshots and a walkthrough. Include candidate → exact path → evidence → declared-control comparison → unknown coverage → optional model explanation.
- Keep precomputed synthetic artifacts and offline report as explicitly labeled fallbacks. Do not fabricate a live scan or model call. Remote hosting is optional unless the portal requires it; publish only synthetic/public-safe data after owner instruction.
- Recommended **feature freeze: Nov 4, 18:00 IST**; **submission target: Nov 4, 23:30 IST**, subject to the owner's verified portal deadline. The public deadline above leaves contingency; Nov 5 morning is not a planned coding window.
- Confirm portal-required repository/demo/video access and save the actual submission receipt. **Done when:** the portal confirms submission, not when a video/file merely exists. No submission is made by this documentation task.

## After the demo — ordered product-expansion gates

### N14 — Establish isolation before any broader intake

Astra defines the threat model and approval gates; Sol implements and tests. Pin a worker environment, read-only source mount, separate restricted output, credential stripping, OS-enforced network restrictions and resource limits; no Docker socket/SSH-agent/host credentials. Test symlink/TOCTOU and crash behavior, output root safety, parser/input/output caps and cancellation. Containerization is defense-in-depth, not a complete guarantee. **Exit:** a reviewed, measured isolation boundary; current process limits do not satisfy it.

### N15 — Expand authorized local intake, then archives

Requires N14 before hostile/untrusted targets. Add explicit ownership/scope allowlists, bounded inventory/exclusions/language diagnostics, dirty/no-Git byte identity, immutable snapshots, retention/deletion rules and safe artifact handling. Add archives only after traversal/symlink/device/decompression/count/size tests; never install target dependencies or run build/test scripts. **Exit:** each intake mode independently reviewed; arbitrary websites/networks remain outside product scope.

### N16 — Improve supported analysis and evaluation incrementally

Expand FastAPI patterns and cross-file semantics one predeclared subset at a time, with positive/safe/unknown regressions and source identity checks. Add compatible Semgrep/CodeQL baselines only after access/license/tier checks; separate advisory matches, reachability and exploitability. Run N09/N10 capability gates before data-flow claims. **Exit:** published support/evaluation matrix for each adapter/rule, without universal coverage claims.

### N17 — Add operational/product features only when required

Prioritize crash/orphan recovery and retention, persisted human triage/events, graph/finding pagination, artifact validation, incremental/diff scans and SARIF against actual user need. Add LangGraph only after linear stages show a concrete state/recovery/concurrency problem; compare it with the existing pipeline and retain deterministic nodes. CI/clean setup, packaging, backup/restore and measured performance precede remote deployment. Remote service then requires auth, tenancy, storage isolation, quotas/queueing and security review. **Exit:** each feature has its own compatibility/migration/tests and owner-approved scope.

### N18 — Broaden research and language/platform coverage

Longer-term backlog: stronger authorization/ownership/tenant relationships and route-variant control inconsistency; dependency advisory/usage/reachability correlation; safe config/secrets metadata; API inventory/deprecated routes; SSRF destination policy, unsafe deserialization, logging and data-disclosure candidate rules with individual evidence gates; more Python frameworks; JavaScript/TypeScript and C/C++ adapters; IaC/cloud IAM; authorized runtime telemetry; business-logic annotations; human false-positive feedback; improved policy/data classification and coverage metrics. Multi-language, graph databases, microservices and a learning loop need measured justification. Automatic exploitation and automatic remediation remain out of scope.

## Practical division of work and stopping rules

| Workstream | Responsibility | Can run alongside |
|---|---|---|
| Owner | Event acceptance/rules, account/key access, budget, license/publication/submission decisions | All independent local work |
| Coordinator + Astra | Contract, priorities, security/privacy decisions and final review | Bounded research after shared interfaces freeze |
| Sol | Artifact loader/provider contracts, backend/tests/evaluation, routine source compatibility | Terra UI against fixed synthetic data |
| Terra | Graph/findings/coverage view, accessibility, demo presentation | Sol provider work after N05 |

A human teammate is not assumed available. Use no more than three concurrent sub-agents initially and keep files separately owned. The two-person split in the original blueprint is a planning option, not an observed team assignment.

**Minimum useful next delivery:** N01–N07 and N12–N13 as applicable, with N08 required only if actual event requirements call for live runtime use and access permits it. N09–N11 are optional; N14–N18 are post-demo unless separately selected. An offline product demo and a qualifying hackathon submission are different outcomes.
