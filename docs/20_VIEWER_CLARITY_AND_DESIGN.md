# 20 — Viewer clarity and graph design

> Team/platform update (2026-11-02): [team handoff](21_TEAM_HANDOFF.md), [finite next-phase plan](22_NEXT_PHASE_PLAN.md), and [current portability/publication evidence](23_PORTABILITY_AND_RELEASE_VERIFICATION.md) supersede earlier onboarding, remote-state and platform assumptions. Historical checks below retain their original date and scope.


This increment refines the existing fixed synthetic demo. The owner's request on **2026-11-02** explicitly selected all three audiences: first-time users/demo judges, developers, and security reviewers. UI UX Pro Max and Impeccable guide the work. Backend analysis, source evidence, packaged bundle identities and model-call defaults remain governed by documents 13 and 16.

## Problem and design intent

The original force-directed graph drew all 23 nodes and 36 relationships at once. Module imports, declarations and candidate paths competed for attention; labels overlapped and identical circles obscured node types. A newcomer had to infer the product's purpose from raw technical details. Evidence was available, but long identity hashes competed with the explanation.

Keep the established navy, blue and amber visual identity. This is an **Operate** surface: reading and verifying an assessment takes priority over decorative motion. The viewer should answer, in order: what does this tool do; which endpoint is selected; what static relationships support the assessment; which source evidence can I inspect; what remains unknown?

## Frozen interaction contract

- A short explanation and three-step guide introduce endpoint selection, static call relationships and source evidence. They supplement the investigator workspace without a blocking tutorial.
- Search and select the six stored endpoints. A candidate badge requires an actual matching finding. All others say **No candidate in this scan**, never Safe, Secure or a policy assertion inferred from a route name.
- Default to the selected finding's exact stored path. Deterministic positioning makes the sequence legible; it does not create a runtime trace or value-flow claim.
- Full graph is an explicit view containing every original node and parallel edge, including declaration/import/module relationships. Node kinds and relationship labels accompany color. All displayed element identities come from the validated bundle.
- Real stored `DEPENDS_ON` relationships are declaration context, with effectiveness unverified. They never become extra steps in the finding's ordered path. `authenticate` and `authorize_export` remain distinct identities.
- Selecting a noncandidate endpoint clears previous finding severity, confidence, explanation and candidate-path details. Its graph may show reachable stored `HANDLES`/`CALLS` structure, labeled as endpoint structure rather than a new finding.
- Graph pan/zoom/fit/reset support exploration. Keyboard-selectable node/path controls and original tables provide alternatives to canvas interaction.
- Inspecting a step shows that real node and relevant stored relationship evidence. Do not relabel all finding evidence as evidence for one step.
- Source locations and readable labels lead; full identities/hashes remain inspectable. PARTIAL coverage, LOW candidate confidence, policy-based severity and mock explanation provenance stay explicit.
- Invalid bundle validation continues to suppress graph, counts and success-shaped controls.

## Research and application

[Cytoscape's layout guidance](https://blog.js.cytoscape.org/2020/05/11/layouts/) describes subgraph selection and positioning as separate decisions. We apply this by showing the exact selected subgraph first and making the full graph an explicit choice. [Cytoscape's preset layout](https://js.cytoscape.org/#layouts/preset) supports deterministic positions without a new layout dependency. The representation remains a graph of static syntax relationships.

[Nielsen Norman Group's progressive-disclosure guidance](https://www.nngroup.com/articles/progressive-disclosure/) informs the separation between first-pass explanation and technical evidence details. Advanced material remains available rather than removed.

UI UX Pro Max's local network-chart guidance identifies accessibility risk and recommends node labels, shapes, relationship summaries and a table/list fallback. Its broad security-product search returned password-manager recommendations that did not match this investigator, so those product/palette suggestions were not applied. React-specific guidance and Impeccable's Operate/craft-floor guidance inform focus states, responsive structure, text contrast and bounded verification. No replacement branding or generic analytics dashboard is introduced.

## Implementation and verification

The graph projection/positioning and shell are separately owned increments against one frozen React interface. Tests must cover exact candidate IDs/order, complete full-graph membership, deterministic placement, endpoint selection with no stale assessment, distinct dependency identities, hostile text and invalid-data suppression. Browser verification checks desktop and 320px layouts, keyboard selection, graph controls and evidence navigation. Motion respects reduced-motion preferences.

The increment is complete. This document does not establish runtime authorization, production detection accuracy or broader intake support.

### Delivered files

- `frontend/src/main.tsx`: explanatory guide, endpoint search/selection, candidate and noncandidate context, node inspection and evidence disclosures.
- `frontend/src/Network.tsx`: Cytoscape rendering, exact path classes, node types, relationship labels and viewport controls.
- `frontend/src/graph-view.ts`: pure deterministic projection and positions; preserves stored parallel identities and never modifies canonical graph objects.
- `frontend/src/style.css`: inherited visual system, responsive canvas heights, local table/list scrolling, focus states, 44px viewport controls and reduced-motion support.
- `main.test.tsx`, `Network.test.tsx`, `graph-view.test.ts`: shell, canvas integration and pure graph regressions. Existing bundle validation tests remain in force.

### Verification — 2026-11-02

**115 backend tests and 16 frontend tests pass.** All nine checks in `scripts/verify_demo.py` pass: backend tests, Ruff check/format, strict mypy, frontend type/lint/tests/build, and shipped bundle validation. Independent read-only Astra review accepted the display semantics and independently ran all 16 frontend tests. SHA256 comparison confirmed all 19 checked backend/package-bundle files unchanged. No dependencies were added and no live model calls were made.

Browser checks confirmed:

- Desktop1440px, mobile320px and720px reflow have matching document/viewport widths.
- Focused view contains the exact four nodes and three relationships of the stored finding; full graph retains23nodes/36relationships, including4real declaration relationships, and highlights only the4candidate nodes/3candidate edges.
- Keyboard Enter on a path step updates the inspected graph node and source references. Zoom increases scale; Reset restores positions/fit; Fit shows the full path.
- Selecting GET /protected clears the previous candidate severity, candidate highlighting and mock explanation, while showing its exact `app.controls.authorize_export` declaration. GET /authenticated retains its separate `app.controls.authenticate` identity.
- Mobile path uses a600px vertical canvas; all four steps remain visible and readable. Endpoint list scrolls within230px; all endpoints remain searchable. Viewport controls have at least44×44px bounds.
- Browser console had no warnings/errors. Eight bounded candidate-switch probes fit all nodes after two animation frames. One earlier zoomed capture showed clipping; Fit restored the complete graph. Panning/zooming can intentionally move elements outside the viewport.

Impeccable's mechanical detector ran once and flagged a thick selected-item side border. The final batch replaced it with a full thin border, removed redundant heading kickers, enlarged graph labels/canvas space and preserved the meaningful three-step guide. Two planned visual passes were followed by a focused check of the clipped capture; no open-ended polish loop was run.

Local evidence: [automated checks](../artifacts/viewer-v2-verification.json), [browser checks](../artifacts/viewer-v2-browser-verification.json), [focused desktop](../artifacts/browser/viewer-v2-desktop.png), [full graph](../artifacts/browser/viewer-v2-overview.png), [mobile](../artifacts/browser/viewer-v2-mobile.png). Screenshots and generated verification artifacts are ignored by Git; source and reproduction commands are committed.

### Use it for each audience

1. **First-time user or demo judge:** read the opening explanation, choose a candidate endpoint, and follow the four visible steps. The amber PARTIAL banner explains the analysis boundary.
2. **Developer:** search a route, select nodes through the graph or step controls, and inspect qualified names and source locations. Switch to Full graph for module, import and dependency context.
3. **Security reviewer:** compare the declaration identities, inspect policy-derived severity and LOW confidence, expand exact node/edge/evidence IDs, read human-review steps and coverage diagnostics. Recorded mock prose remains visibly UNREVIEWED assistance.

### Limits and next checks

The fixed23-node corpus is the only measured UI dataset; no large-graph usability or external-user study is claimed. Full graph becomes dense at narrow widths: use the focused path, zoom controls and keyboard/table alternatives. Native browser zoom and a screen-reader session were not tested;720px reflow and keyboard behavior were tested. The existing approximately840kB production chunk warning remains; code splitting should be evaluated against measured loading cost before adding dependencies or changing the bundle contract. Live-provider, event/submission, analyzer and hostile-intake gates from document19 are unchanged.

Future refinements should begin with actual user feedback or measured rendering/loading issues. Preserve exact graph identities, conservative noncandidate labels and the validated fixed-bundle boundary when extending the experience.
