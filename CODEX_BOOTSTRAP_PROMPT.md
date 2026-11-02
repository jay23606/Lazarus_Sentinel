# Continue Lazarus Sentinel — do not restart the completed first slice

Read AGENTS.md, AGENT.md, README.md, docs/13_FIRST_SLICE_CONTRACT.md, docs/14_IMPLEMENTATION_REVIEW.md, docs/15_NEXT_STEPS.md and TASK_BOARD.md. Inspect current source/tests before changes. Documents 00–12 distinguish implemented facts from later proposals.

## Current state

The fixture-only AST → normalized graph → LS-AUTH-001 → SQLite/JSON/Markdown pipeline is complete. Last verified baseline: 73 tests, clean Ruff/mypy, 6 endpoints, 23 nodes, 36 edges, 2 LOW-confidence candidates and 3 matching authorization declarations with unverified effectiveness. PARTIAL/exit 2 is intentional for seeded dynamic registration. Astra approved the bounded implementation and escaped report display.

Do not rerun initial setup/research as new work, duplicate the detector implementation, or infer a failed Joern spike. Joern remains NOT_ATTEMPTED; data/trust rules NOT_IMPLEMENTED. No Git repository, UI, HTTP API, LangGraph or live LLM provider exists.

## Next work selection

Use task IDs N01–N18 in docs/15_NEXT_STEPS.md. The recommended next delivery is a fixed validated artifact viewer plus optional evidence-bounded explanations; event/provider prerequisites come first. This is a recommendation, not blanket implementation approval. Execute only the next increment the owner actually selects.

1. Check the live ledger and task board; retain completed and deferred distinctions.
2. Resolve external requirements/access without exposing credentials or inventing account eligibility.
3. Freeze the chosen increment's interfaces and acceptance criteria before delegating work.
4. Reuse schema 0.1.0, exact evidence identities, byte-manifest provenance and the working CLI/report path.
5. Add focused regressions, run relevant checks, and get Astra review for security-sensitive changes.
6. Update AGENT.md, decisions, task board and affected docs with measured results and unresolved gates.

## Invariants

- Only `lazarus scan --target fixture:fastapi-demo` is currently supported. No arbitrary source paths, uploads or external targets.
- CALLS is not data flow. Policy-defined sensitivity is a human assertion. Observed DEPENDS_ON is a declaration, not proven authorization. Opaque controls/unresolved paths are diagnostics only.
- Keep severity, confidence, verification status and coverage separate. Never silently confirm a candidate.
- Provider credentials do not enable egress. Any later call requires its own reviewed configuration and authorization; start with minimal synthetic data.
- Follow AGENTS.md model routing: Astra for critical/security judgments, Sol for routine implementation, Terra for UI. Use actual supported labels; no invented coordinator identity.
- No global installs, target execution, exploit generation, automatic remediation, unrequested publication or submission.
- Preserve historical scan artifacts and append-only session notes. Report what was verified, partial, blocked or deferred.
