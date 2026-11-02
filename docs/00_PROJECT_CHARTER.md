# 00 — Project Charter

## Integrated demo status — 2026-11-02

The approved [demo contract](16_DEMO_DELIVERY_CONTRACT.md) is implemented alongside the preserved first-slice analyzer: immutable hash-verified bundles, disabled/mock explanations with a gated Meta adapter, and a fixed React/Vite/TypeScript/Cytoscape viewer. See [capability gates](17_CAPABILITY_AND_RESEARCH_REPORT.md), [finite evaluation](18_DEMO_EVALUATION.md), and [integrated verification](19_INTEGRATED_DEMO_REVIEW.md) for current checks and review disposition. Document 14 remains historical first-slice evidence; its 73-test count is not the integrated total.

Local baseline commit `7797b85` is preserved on `feat/integrated-demo`; no remote, publication, submission or license selection is implied. Only fixed synthetic intake is supported. Live access is BLOCKED by the missing key; zero paid calls were made. Joern setup is blocked and analysis NOT_ATTEMPTED; data/trust rules remain NOT_IMPLEMENTED. OS sandbox launch failed before execution, so broader intake remains blocked.

## Product objective

**Lazarus Sentinel — Graph-First Application Security Intelligence** correlates program structure, application architecture and security context to produce reproducible candidate findings for human review. Its intended contribution is evidence-backed correlation across paths, rather than graph drawing or a scanner chatbot. The product is defensive and read-only: no exploitation, target modification or automatic remediation.

## Delivered scope

The implemented product is one controlled synthetic FastAPI fixture analyzed through Python AST without importing or executing its code. The CLI builds a normalized graph, evaluates policy-defined authorization declaration context with LS-AUTH-001, and writes SQLite metadata plus JSON/Markdown artifacts. It does not accept arbitrary repositories or archives.

The measured result is six supported endpoints, 23 nodes, 36 edges, two LOW-confidence candidates and three matching authorization declarations whose effectiveness is unverified. Seeded dynamic registration deliberately yields PARTIAL coverage. These counts demonstrate reproducibility on this fixture, not detection accuracy on real applications.

## Longer-term product thesis

The intended audience is developers and security engineers reviewing authorized applications. The future journey is authorized intake → evidence graph → candidate path → coverage-aware human review. Program/data-flow facts, identities, roles, sensitive assets, trust boundaries, external services and controls are useful future graph layers only when supported by deterministic evidence or explicit human provenance.

Broader analysis adapters, data/trust rules, HTTP API and verified live runtime model access remain roadmap capabilities. The fixed graph viewer and disabled/mock explanation boundary are delivered under document 16. Joern is NOT_ATTEMPTED; LS-DATA-001 and LS-TRUST-001 are NOT_IMPLEMENTED. None is mandatory to complete the already-approved first slice.

## Success and non-goals

Judge future increments by useful, traceable findings and explicit unknowns on declared benchmarks. Do not promise complete runtime graphs, confirmed vulnerabilities, generalized accuracy, superiority over established analyzers from synthetic tests. Keep severity, confidence and coverage separate.

Hackathon participation and a meaningful Meta runtime capability are separate readiness gates. No provider is enabled in the current product. Event access, deadline, eligibility, terms and required deliverables must be verified against current organizer information before submission; see the next-step checklist and sources register.
