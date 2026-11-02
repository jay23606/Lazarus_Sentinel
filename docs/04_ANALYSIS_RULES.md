# 04 — Analysis Engine and Security Rules

## Integrated demo status — 2026-11-02

The approved [demo contract](16_DEMO_DELIVERY_CONTRACT.md) is implemented alongside the preserved first-slice analyzer: immutable hash-verified bundles, disabled/mock explanations with a gated Meta adapter, and a fixed React/Vite/TypeScript/Cytoscape viewer. See [capability gates](17_CAPABILITY_AND_RESEARCH_REPORT.md), [finite evaluation](18_DEMO_EVALUATION.md), and [integrated verification](19_INTEGRATED_DEMO_REVIEW.md) for current checks and review disposition. Document 14 remains historical first-slice evidence; its 73-test count is not the integrated total.

Local baseline commit `7797b85` is preserved on `feat/integrated-demo`; no remote, publication, submission or license selection is implied. Only fixed synthetic intake is supported. Live access is BLOCKED by the missing key; zero paid calls were made. Joern setup is blocked and analysis NOT_ATTEMPTED; data/trust rules remain NOT_IMPLEMENTED. OS sandbox launch failed before execution, so broader intake remains blocked.

## Implemented LS-AUTH-001

The rule assesses whether a policy-required authorization function declaration is recognized along a supported endpoint-to-protected-operation structural path. Operator-authored `policy.json` supplies exact qualified identities, severity/impact assumptions and author/time provenance. The separate expected-results oracle is not read by the analyzer.

| Condition | Result |
|---|---|
| Supported path/control scope with matching required declaration | Suppress candidate; effectiveness remains unverified |
| Supported path/control scope without recognized required declaration | LOW-confidence CANDIDATE / NEEDS_REVIEW / POTENTIAL_GAP |
| Opaque control scope, unresolved path or ambiguous symbol | NEEDS_CONTEXT diagnostic only |
| Operation has no operator policy | No candidate or sensitivity guess |

Authentication alone does not satisfy a policy requiring authorization. Declarations from supported app/router/include/decorator/parameter scopes use observed DEPENDS_ON edges. They do not become claims of successful enforcement. Unsupported middleware, factories, subdependencies, aliases and dynamic behavior are handled conservatively under the contract.

Every candidate carries rule/version, repository revision, ordered node/edge path, evidence IDs, policy impact hypothesis, assumptions, unknowns, false-positive considerations and human review steps. `Finding` in `models.py` is authoritative. Severity reflects policy-assumed impact; LOW confidence reflects limited declaration evidence; coverage records supported scope separately. No exploitability score or confirmed status is implemented.

The measured fixture produces candidates for GET /weak and GET /authenticated, recognizes three matching declarations with effectiveness unverified, and leaves the public/no-policy path unflagged. Dynamic registration remains a coverage diagnostic.

## Future rule families — NOT_IMPLEMENTED

**LS-DATA-001:** candidate untrusted/sensitive flow to a classified sink. Requires actual value-propagation evidence, source/sink definitions, control semantics and a tested uncertainty policy. CALLS edges cannot substitute for taint/data flow.

**LS-TRUST-001:** candidate handling gap across an explicitly modeled trust boundary. Requires a documented expected-handling policy, boundary evidence and uncertainty treatment. Crossing a boundary alone is not a vulnerability.

Dependency advisory correlation, configuration/secrets analysis, access-control inconsistencies, logging exposure and cloud/runtime context are later ideas. No common GraphRule protocol is implemented. The explanation pipeline validates references without adjudicating finding truth; freeze new detector interfaces only for a selected increment.

## Model interpretation guardrails

The optional explanation provider may explain supplied evidence or identify missing context. It may not invent graph/source facts, establish absent controls from missing extraction, confirm vulnerabilities, execute payloads or modify targets. Schema/evidence-reference validation and minimized synthetic context are implemented under document 16; live account/privacy verification remains blocked. Threat-category/ASVS mappings require verified source identifiers; none should be guessed.
