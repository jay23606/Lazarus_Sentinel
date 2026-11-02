# 19 — Integrated demo delivery and verification

Verified **2026-11-02**. The fixed synthetic demo is implemented and independently reviewed. This completes the bounded offline delivery, with explicit external and capability gates below. It does not complete a hackathon submission or the open-ended platform roadmap.

Subsequent UI refinement: [document20](20_VIEWER_CLARITY_AND_DESIGN.md) records the newer guided graph interface and16frontend tests. The8-test result below is the preserved original integrated-demo checkpoint.

## Delivered workflow

1. `uv sync --project backend --locked` creates the Python 3.13.14 project environment.
2. `backend/.venv/bin/lazarus scan --target fixture:fastapi-demo` creates a new immutable scan. Expected exit **2** means **PARTIAL**, because dynamic route registration is deliberately unsupported.
3. `backend/.venv/bin/lazarus explain --scan-id <UUID> --finding-id <ID>` defaults to **disabled**. Explicit `--provider mock` records a separate deterministic annotation. Explicit `meta` exists but live verification is blocked by missing credentials.
4. `backend/.venv/bin/lazarus demo export --scan-id <UUID> [--annotation-id <UUID>]` verifies committed artifacts and current fixture evidence before publishing a new immutable bundle.
5. `cd frontend && npm ci --ignore-scripts --no-audit --no-fund && npm run dev` serves the fixed reviewed assets at `http://127.0.0.1:5173/`. No uploads, arbitrary URLs or backend API are exposed.

`backend/.venv/bin/python scripts/prepare_demo.py` repeats scan → disabled check → mock annotation → verified export → fixed viewer assets. It creates fresh identities and checks that canonical graph bytes and the live budget remain unchanged. Replacing packaged assets is a development operation; original scans and exports remain immutable.

Packaged scan: `d4788c12-b956-4535-b897-13744439093e`. Bundle: `f85376c4-9ec1-4b8f-aea2-1c0f89abae3e`. Annotation: `0f517df7-2713-4dff-87c1-cb0166b63f8d` (**recorded mock**, not live).

## Verification results

| Check | Result |
|---|---|
| Full backend pytest | **115 passed**; original 73-test baseline preserved |
| Python checks | Ruff check and format pass across backend source/tests and scripts; strict mypy passes |
| Frontend | **8 tests passed**, TypeScript, ESLint and production build pass |
| Clean-copy reproduction | Fresh source copy with new locked Python environment and clean npm installation; all nine offline checks pass; not a hosted CI run |
| Full offline verification | All nine checks in `scripts/verify_demo.py` pass, including shipped bundle validation |
| Repeat scans | Two fresh graphs byte-identical: **23 nodes, 36 edges, 2 findings**; both PARTIAL |
| Fixture interpretation | **6 endpoints**, 2 LOW-confidence candidates, 3 matching declarations with effectiveness unverified; public path unflagged; unsupported registration visible |
| Independent Astra review | No material issue remaining in the fixed synthetic demo; 40 focused backend tests and 8 frontend tests independently passed |
| Browser | Desktop 1440px and mobile 320px have no document overflow; tables scroll within wrappers; graph canvas resizes; keyboard Enter selects the exact stored 4-node/3-edge path |
| 200% reflow | Tested with equivalent CDP viewport/DPR metrics, **not native browser zoom** |
| Live model usage | **Zero live attempts / US$0**; credentials absent; disabled/mock paths do not consume budget |

Backend gates cover artifact corruption/mirror disagreement, duplicate IDs, references/paths/revisions, source changes, annotation bindings, unknown citations/field changes, provider failure/deadline, and transactional budget concurrency. Frontend gates cover hashes/schemas/versions, status agreement, node/edge identity collisions, selection, text escaping and invalid-data suppression. Tests establish the specified behavior, not general security efficacy.

Machine-readable local evidence (generated, ignored by Git): [integration checks](../artifacts/integration-verification.json), [repeat scans](../artifacts/repeat-scan-verification.json), [clean-copy checks](../artifacts/clean-copy-verification.json). Screenshots: [desktop](../artifacts/browser/final-desktop.png), [mobile](../artifacts/browser/final-mobile.png). These links require the local evidence directory; portable source includes the synthetic viewer bundle and reproduction scripts.

## Independent review and limits

Astra accepted read-only committed-artifact loading, exact hashes/mirrors/current-source verification, immutable annotation binding, default-disabled bounded context, citation checks, transactional reservations, five-attempt cap, fail-closed ambiguous usage, killable deadline, no redirects/retries, and viewer textual rendering/path validation/error suppression. No live requests were made during review.

Hashes establish consistency with the reviewed manifest, not authenticity if an attacker replaces the manifest and payloads together. Concurrent hostile filesystem replacement and arbitrary-repository isolation remain outside approval. Model citation validation does not prove prose factuality. The Standard-mode adapter is not a zero-retention guarantee. Prices are recorded as verified Nov 2 and must be rechecked before later live use; the cap covers this application's ledger, not unrelated account spending.

The production frontend emits an approximately **831 kB** chunk warning. The fixed graph is bounded to 500 nodes/2,000 edges and 1 MiB total; no large-repository performance claim follows. Native browser zoom, hosted CI, remote deployment and live Meta access are unverified.

## N01–N18 disposition and next actions

| ID | Status and remaining gate |
|---|---|
| N01 | **BLOCKED externally:** owner acceptance, portal rules, required technology and submission fields unconfirmed |
| N02 | **BLOCKED externally:** no configured credential/account verification; no paid request |
| N03 | **Local baseline DONE:** commit `7797b85`, feature branch; license selection and remote publication pending owner decision |
| N04 | **DONE:** separate policy/oracle, baseline and three controlled evaluation variants; no general accuracy claim |
| N05 | **DONE:** approved [bundle/explanation/viewer contract](16_DEMO_DELIVERY_CONTRACT.md) |
| N06 | **DONE:** fixed graph/findings/coverage viewer and accessible tables |
| N07 | **DONE:** default-disabled/mock explanation boundary and hostile-output checks |
| N08 | **Adapter implemented, live BLOCKED:** stub transport/deadline/budget checks pass; access and exact live narrative remain unverified |
| N09 | **SETUP_BLOCKED:** pinned Joern release/JDK/platform preflight recorded; analyzer **NOT_ATTEMPTED**; no capability failure inferred |
| N10 | **NOT_IMPLEMENTED:** DATA/TRUST lack demonstrated value-flow/boundary-policy gates; no substitute call-flow claims |
| N11 | **SKIPPED:** fixed asset loading satisfies demo; HTTP API unnecessary |
| N12 | **DONE for offline profile:** integrated checks, browser validation and independent review pass |
| N13 | **Local materials READY; submission BLOCKED:** no portal receipt, publication, video submission or eligibility claim |
| N14 | **BLOCKED:** sandbox runtime launch denied; filesystem/network/resource isolation not established |
| N15 | **BLOCKED by N14:** no arbitrary local/archive intake added |
| N16 | **Finite evaluation pilot DONE; broader expansion OPEN:** existing semantics preserved; no licensed scanner comparison executed |
| N17 | **Finite operations tranche DONE:** read-only artifact inspection, local clean setup, credential-free CI configuration; hosted CI and later workflow features remain open |
| N18 | **Finite research tranche DONE:** complete catalogue and DATA/TRUST evidence matrices; language/detector implementation program remains open |

Continue in this order: confirm organizer requirements and account access; select license/publication terms; verify fresh pricing and one explicitly selected bounded synthetic Meta request; review its exact narrative; rehearse required submission materials; obtain a real portal receipt. After the demo, choose an approved isolation runtime and pass N14 before N15. Keep DATA/TRUST deferred until their independent evidence gates pass. See [capability report](17_CAPABILITY_AND_RESEARCH_REPORT.md), [evaluation](18_DEMO_EVALUATION.md) and [ordered roadmap](15_NEXT_STEPS.md).
