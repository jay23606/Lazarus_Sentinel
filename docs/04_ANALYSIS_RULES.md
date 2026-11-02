# 04 — Analysis Engine and Security Rules

Current implementation is governed by the [approved first-slice contract](13_FIRST_SLICE_CONTRACT.md). [Verified results](14_IMPLEMENTATION_REVIEW.md) describe the measured fixture run; [ordered next steps](15_NEXT_STEPS.md) are proposals for subsequent work, not approval to implement them.

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

Dependency advisory correlation, configuration/secrets analysis, access-control inconsistencies, logging exposure and cloud/runtime context are later ideas. No common GraphRule protocol or model-review pipeline is implemented; freeze future interfaces only when a bounded increment is selected.

## Future model interpretation guardrails

A future model may explain supplied evidence or identify missing context. It may not invent graph/source facts, establish absent controls from missing extraction, confirm vulnerabilities, execute payloads or modify targets. Schema and evidence-reference validation, redaction and egress review are prerequisites, not existing capabilities. Threat-category/ASVS mappings require verified source identifiers; none should be guessed.
