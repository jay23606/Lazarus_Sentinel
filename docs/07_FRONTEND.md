# 07 — Reporting Experience and Frontend Roadmap

Current implementation is governed by the [approved first-slice contract](13_FIRST_SLICE_CONTRACT.md). [Verified results](14_IMPLEMENTATION_REVIEW.md) describe the measured fixture run; [ordered next steps](15_NEXT_STEPS.md) are proposals for subsequent work, not approval to implement them.

## Current user experience

There is no frontend application, browser graph or HTTP API. The usable experience is the fixture-only CLI followed by generated JSON and escaped Markdown reports. The [verified implementation review](14_IMPLEMENTATION_REVIEW.md) links the latest report and measurements.

The report presents source revision, coverage/diagnostics, endpoint labels, ordered structural paths and declared dependencies. Evidence retains relative locations/hashes rather than source excerpts. Candidates remain CANDIDATE / NEEDS_REVIEW / POTENTIAL_GAP with LOW confidence; matching dependency declarations explicitly have effectiveness unverified. Human review occurs outside an application triage workflow.

Current demonstration: run the fixture scan, explain expected exit 2/PARTIAL, inspect GET /weak and GET /authenticated candidates, compare recognized declarations and the unflagged public/no-policy path, then show unsupported dynamic registration. Repeat graph equality and artifact hashes support reproducibility; no data-flow or runtime-security claim follows.

## Future frontend — proposed only

React + Vite + TypeScript with Cytoscape.js is a possible presentation stack. No dependency versions or package scaffold have been selected/installed. Verify compatibility before a selected UI increment; agree API/artifact contracts before parallel implementation.

Useful future views:

- Scan overview: revision, status, timing, graph counts, findings and explicit coverage gaps.
- Application graph: evidence-backed nodes/edges, search/filter, local neighborhoods and selected candidate path.
- Findings/detail: separate severity/confidence/verification, observation versus hypothesis, source ranges/hashes, assumptions, unknowns and review actions.
- Coverage/diagnostics: supported, partial, failed, skipped and unsupported scope with reasons.

A future triage UI depends on a new persistence/auth contract. Source excerpt display depends on a separately defined retention/access policy. Do not portray these features as present.

## UX acceptance guidance for future work

The graph should support investigation, with a table/report alternative, keyboard access and status labels beyond color. Cap initial elements, expand neighborhoods and avoid expensive repeated layouts. Explain every relationship through evidence and keep uncertainty visible.

Use “candidate,” “no matching declaration was recognized,” and “partially analyzed.” Avoid “confirmed vulnerability,” “no authorization exists,” “secure comparison path,” or qualitative confidence presented as a calibrated probability. Demonstrations should use reproducible fixture output, not fabricated findings or a required live model response.

Cytoscape.js reference for future evaluation: https://js.cytoscape.org/
