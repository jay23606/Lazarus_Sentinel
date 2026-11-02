# 00 — Project Charter

Current implementation is governed by the [approved first-slice contract](13_FIRST_SLICE_CONTRACT.md). [Verified results](14_IMPLEMENTATION_REVIEW.md) describe the measured fixture run; [ordered next steps](15_NEXT_STEPS.md) are proposals for subsequent work, not approval to implement them.

## Product objective

**Lazarus Sentinel — Graph-First Application Security Intelligence** correlates program structure, application architecture and security context to produce reproducible candidate findings for human review. Its intended contribution is evidence-backed correlation across paths, rather than graph drawing or a scanner chatbot. The product is defensive and read-only: no exploitation, target modification or automatic remediation.

## Delivered scope

The implemented product is one controlled synthetic FastAPI fixture analyzed through Python AST without importing or executing its code. The CLI builds a normalized graph, evaluates policy-defined authorization declaration context with LS-AUTH-001, and writes SQLite metadata plus JSON/Markdown artifacts. It does not accept arbitrary repositories or archives.

The measured result is six supported endpoints, 23 nodes, 36 edges, two LOW-confidence candidates and three matching authorization declarations whose effectiveness is unverified. Seeded dynamic registration deliberately yields PARTIAL coverage. These counts demonstrate reproducibility on this fixture, not detection accuracy on real applications.

## Longer-term product thesis

The intended audience is developers and security engineers reviewing authorized applications. The future journey is authorized intake → evidence graph → candidate path → coverage-aware human review. Program/data-flow facts, identities, roles, sensitive assets, trust boundaries, external services and controls are useful future graph layers only when supported by deterministic evidence or explicit human provenance.

Broader analysis adapters, data/trust rules, API/UI, optional graph visualization and a bounded runtime model explainer remain roadmap capabilities. Joern is NOT_ATTEMPTED; LS-DATA-001 and LS-TRUST-001 are NOT_IMPLEMENTED. None is mandatory to complete the already-approved first slice.

## Success and non-goals

Judge future increments by useful, traceable findings and explicit unknowns on declared benchmarks. Do not promise complete runtime graphs, confirmed vulnerabilities, generalized accuracy, superiority over established analyzers from synthetic tests. Keep severity, confidence and coverage separate.

Hackathon participation and a meaningful Meta runtime capability are separate readiness gates. No provider is enabled in the current product. Event access, deadline, eligibility, terms and required deliverables must be verified against current organizer information before submission; see the next-step checklist and sources register.
