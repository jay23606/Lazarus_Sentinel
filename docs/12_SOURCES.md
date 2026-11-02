# 12 — Sources and Technical References

## Integrated demo status — 2026-11-02

The approved [demo contract](16_DEMO_DELIVERY_CONTRACT.md) is implemented alongside the preserved first-slice analyzer: immutable hash-verified bundles, disabled/mock explanations with a gated Meta adapter, and a fixed React/Vite/TypeScript/Cytoscape viewer. See [capability gates](17_CAPABILITY_AND_RESEARCH_REPORT.md), [finite evaluation](18_DEMO_EVALUATION.md), and [integrated verification](19_INTEGRATED_DEMO_REVIEW.md) for current checks and review disposition. Document 14 remains historical first-slice evidence; its 73-test count is not the integrated total.

Local baseline commit `7797b85` is preserved on `feat/integrated-demo`; no remote, publication, submission or license selection is implied. Only fixed synthetic intake is supported. Live access is BLOCKED by the missing key; zero paid calls were made. Joern setup is blocked and analysis NOT_ATTEMPTED; data/trust rules remain NOT_IMPLEMENTED. OS sandbox launch failed before execution, so broader intake remains blocked.

> Initial source register prepared **2026-11-01**; documentation refreshed **2026-11-02**. Only the event page, Meta overview and pricing/mode pages were reopened in this refresh (section I); other links retain their earlier verification scope. Prefer primary documentation. Before implementation, Codex must reopen relevant docs to verify current APIs, install steps, compatibility, licensing, model IDs, and terms. Do not treat a web search snippet as a complete specification.

## A. Core graph/static-analysis foundations

### S01 — Joern documentation

https://docs.joern.io/

Use for: Code Property Graphs, language frontends, CPG layers, taint analysis, queries, export and CLI behavior. Joern documents source/bytecode/binary analysis and a CPG representation; it lists Python, JavaScript and C/C++ frontends with varying maturity. It is a candidate tool, not a guarantee that every FastAPI semantic is extracted.

Relevant pages:
- CPG: https://docs.joern.io/code-property-graph/
- Quickstart: https://docs.joern.io/quickstart/
- Export: https://docs.joern.io/export/
- Python frontend: linked from https://docs.joern.io/ under Frontends.

### S02 — CodeQL documentation

https://codeql.github.com/docs/

Use for: semantic code queries, data-flow/taint analysis and path queries. Consider as an alternative or comparison baseline; confirm supported language and CLI licensing/availability for the project's use case.

### S03 — Semgrep documentation

https://semgrep.dev/docs/

Use for: pattern-based static analysis and taint-mode rules. Important qualification: cross-function and cross-file behavior depends on product tier, language support, and rule configuration. Check the current feature matrix before describing coverage.

### S04 — Original Code Property Graph research

Yamaguchi et al., “Modeling and Discovering Vulnerabilities with Code Property Graphs,” IEEE Symposium on Security and Privacy (2014).

Reference/search starting points:
- https://ieeexplore.ieee.org/document/6956589 (confirm access/metadata)
- Joern project/docs: https://docs.joern.io/

Use for: conceptual foundation combining syntax, control-flow and program-dependence information. The existence of CPG research means Lazarus Sentinel's novelty must be in application/security-context correlation, coverage and evidence-centered workflow, not graph construction alone.

## B. Application security and threat modeling

### S05 — OWASP Threat Modeling Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html

Use for: threat modeling, data-flow diagrams, trust boundaries, STRIDE and risk identification.

### S06 — OWASP API Security Top 10

https://owasp.org/www-project-api-security/

Developer guide: https://devguide.owasp.org/en/07-training-education/07-api-top-ten/

Use for: API risks including Broken Object Level Authorization, Broken Authentication, Broken Object Property Level Authorization, resource consumption, Broken Function Level Authorization, sensitive business flows, SSRF, misconfiguration, inventory and unsafe API consumption.

### S07 — OWASP ASVS 5.0.0

https://asvs.owasp.org/

Downloads: https://asvs.owasp.org/downloads/

GitHub source of truth: https://github.com/OWASP/ASVS

Use for: application-security verification requirements. Stable version identified by OWASP as 5.0.0. Verify requirement IDs against the selected stable release and version them in findings.

### S08 — OWASP Developer Guide / secure development

https://devguide.owasp.org/

Use for: developer-facing security engineering guidance. Static analysis is one component of a layered security process; do not rely on one analyzer alone.

### S09 — NIST SP 800-218 SSDF v1.1

https://csrc.nist.gov/pubs/sp/800/218/final

Use for: secure software development lifecycle practices, reducing vulnerabilities and addressing root causes. Published February 2022; verify whether a newer revision or companion guidance exists before a formal compliance claim.

## C. Graph processing, frontend, and application framework

### S10 — NetworkX documentation

https://networkx.org/documentation/stable/

Use for: in-memory graph representation, path queries, traversal and graph algorithms in the MVP. Keep serialized JSON as the portable canonical artifact rather than pickling NetworkX objects.

### S11 — Cytoscape.js documentation

https://js.cytoscape.org/

Use for: interactive browser graph visualization, filtering, selecting and highlighting paths. Check license and current version before adoption.

### S12 — FastAPI documentation

https://fastapi.tiangolo.com/

Use for: route definitions, dependency injection and framework integration. The extractor should support only patterns covered by tests and should report dynamic/unrecognized patterns as unknown.

### S13 — Python `ast` documentation

https://docs.python.org/3/library/ast.html

Use for: fallback deterministic parsing of Python syntax, decorators, function definitions, imports and basic call relationships. Python AST alone is not a full semantic/interprocedural/data-flow engine.

## D. Interchange and evaluation

### S14 — SARIF 2.1.0 (OASIS)

https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/sarif-v2.1.0-os.html

OASIS archive: https://www.oasis-open.org/standards/

Use for: standardized static-analysis result interchange, optional report export once the finding model is stable.

### S15 — OWASP Benchmark

https://owasp.org/www-project-benchmark/

Use for: evaluating static-analysis detection accuracy, coverage and speed. It includes runnable vulnerable test cases in Java and Python. Confirm compatibility and scope before using it as a headline benchmark.

## E. Isolation and secure execution

### S16 — Docker rootless mode

https://docs.docker.com/engine/security/rootless/

Use for: running daemon/containers without root privileges where supported.

### S17 — Docker resource constraints

https://docs.docker.com/engine/containers/resource_constraints/

Use for: setting CPU/memory limits on analyzer workers. Verify support on the local platform.

### S18 — Docker seccomp

https://docs.docker.com/engine/security/seccomp/

Use for: syscall restriction. Container isolation is defense-in-depth, not a complete guarantee.

## F. Codex, models, MCP and skills

### S19 — Codex prompting guide / AGENTS.md

https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide

Use for: Codex instruction-file behavior and repository-specific guidance. `AGENTS.md` is the recognized persistent instruction filename; keep the separate `AGENT.md` project log requested by the owner.

### S20 — OpenAI model selection guide

https://developers.openai.com/api/docs/guides/model-selection

Use for: official model-selection guidance when needed. The owner-specific Astra/Sol/Terra routing is defined in AGENTS.md and actual exercised runtime identifiers are recorded in AGENT.md. This page was not reopened in the 2026-11-02 documentation refresh; do not infer account entitlement, availability or current model taxonomy from this register.

### S21 — OpenAI reasoning models guide

https://developers.openai.com/api/docs/guides/reasoning

Use for: reasoning model selection and effort. Do not assume every runtime exposes every model or effort option.

### S22 — OpenAI multi-agent guide

https://developers.openai.com/api/docs/guides/agents-api/multi-agent

Use for: delegation to independent sub-agents, parallel context and concurrency guidance. The guide notes that subagents are best for independent tasks and warns that agents editing the same files need coordination. Use the Codex runtime's supported delegation features; do not assume API-specific configuration works in the IDE/CLI.

### S23 — OpenAI Docs MCP

https://developers.openai.com/learn/docs-mcp

Use for: current OpenAI/Codex documentation through an MCP server. The public documentation describes `codex mcp add ...` and `codex mcp list`; use an existing configured server first and do not add a new server without owner approval.

### S24 — Skills concept

https://developers.openai.com/plugins/concepts/skills

Use for: skills as folders of instructions/resources that complement MCP tools. Inspect existing `SKILL.md` files and invoke only relevant installed skills.

## G. Meta Model API / Hackathon

### S25 — Meta Global AI Developer Hackathon

https://dev.meta.ai/events/global-hackathon

Use for: current event themes, model/tool requirements, dates, tracks and official rules. Recheck immediately before submission.

### S26 — Meta Model API overview

https://dev.meta.ai/products/meta-model-api

Use for: official developer access to Meta models and current availability/terms.

### S27 — Meta Model API documentation overview

https://dev.meta.ai/docs/overview

Use for: current API base URL, authentication, supported SDK formats, model names, and capabilities. The current overview describes Muse Spark model IDs and an OpenAI-compatible API surface. Verify current values before implementation.

### S28 — Build with Muse Spark / Meta Model API

https://dev.meta.ai/resources/blog/build-with-muse-spark

Use for: API examples and agentic integration patterns. The page is a guide, not a substitute for checking the current API reference.

## Source-use rules

- Prefer official docs and standards for API behavior and requirements.
- Pin software versions and note the date checked.
- Do not claim a scanner feature is available in a free/community edition without checking current docs.
- Do not infer model availability or pricing from old blog posts.
- Add sources to this file whenever a new dependency, standard, analyzer rule or integration is adopted.

## H. First-slice dependency preflight — checked 2026-11-01

- Pydantic installation: https://pydantic.dev/docs/validation/latest/get-started/install/
- NetworkX install / supported Python: https://networkx.org/documentation/stable/install.html
- uv locking/syncing: https://docs.astral.sh/uv/concepts/projects/sync/

The local CPython 3.13.14 environment resolved Pydantic 2.14.2, NetworkX 3.7, pytest 9.2.0, Ruff 0.17.3 and mypy 1.20.2. Exact dependency versions/hashes are recorded in backend/uv.lock. Network access was used only to install approved implementation dependencies, not to analyze targets. Sandbox DNS blocked the first install; the same project-local sync succeeded with network permission. No global packages/tools were installed.

## I. Next-step planning source refresh — reopened 2026-11-02

| Source | What was confirmed | What remains unknown |
|---|---|---|
| https://dev.meta.ai/events/global-hackathon | Public event page lists Nov 4, 9:00 PM ET = Nov 5, 7:30 AM IST; selected-participant event; dates may change | Owner acceptance, organizer portal rules/requirements, track/team eligibility, submission receipt |
| https://dev.meta.ai/docs/overview | Base https://api.meta.ai/v1; MODEL_API_KEY; documented Standard Muse Spark IDs muse-spark-1.3 / 1.2 / 1.1 | Actual account/model/region access, quota/billing, approved spend and successful request |
| https://dev.meta.ai/docs/pricing-rate-limits | Standard mode does not use content for training; Contributor variants permit submitted content for training | No zero-retention guarantee established; actual selected integration/privacy approval |

This is read-only primary-source verification, not an API/model test or an assertion of event eligibility. Retain Muse Spark as the intended provider family; do not silently switch to another model because the general overview also advertises other models. Recheck exact model/request compatibility and terms when a live adapter is selected. No keys, account secrets or source were sent.

The full recommended sequence is [15_NEXT_STEPS.md](15_NEXT_STEPS.md). Implemented results are in [14_IMPLEMENTATION_REVIEW.md](14_IMPLEMENTATION_REVIEW.md); current scope is [13_FIRST_SLICE_CONTRACT.md](13_FIRST_SLICE_CONTRACT.md).


## Viewer clarity research — 2026-11-02

- [Cytoscape layout guide](https://blog.js.cytoscape.org/2020/05/11/layouts/) and [preset layout documentation](https://js.cytoscape.org/#layouts/preset): opened for selected-subgraph and deterministic-position design; implementation retains the installed dependency/lock.
- [Nielsen Norman Group: Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/): opened for first-pass guidance versus deeper evidence.
- Owner-requested local UI UX Pro Max chart/React guidance and Impeccable Operate/craft-floor/context/detector workflow applied; no new plugin/global installation. See [design decisions and verification](20_VIEWER_CLARITY_AND_DESIGN.md).
