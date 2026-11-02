# 02 — System Architecture

Current implementation is governed by the [approved first-slice contract](13_FIRST_SLICE_CONTRACT.md). [Verified results](14_IMPLEMENTATION_REVIEW.md) describe the measured fixture run; [ordered next steps](15_NEXT_STEPS.md) are proposals for subsequent work, not approval to implement them.

## Implemented modular monolith

```mermaid
flowchart TD
    CLI[Fixture-only argparse CLI] --> IN[Bounded manifest and byte snapshot]
    IN --> W[Deadline-bounded AST child worker]
    W --> G[Normalized graph and coverage]
    G --> R[LS-AUTH-001 with operator policy]
    R --> V[Evidence validation and source recheck]
    V --> A[Stage JSON and escaped Markdown]
    A --> P[Rename artifacts then commit SQLite references]
```

The implementation is a small Python package under `backend/src/lazarus_sentinel/`, not the earlier proposed layered API/frontend tree. `models.py` owns strict Pydantic envelopes; `intake.py` bounds reads; `worker.py` launches extraction; `analysis.py` extracts supported structure; `rules.py` evaluates declarations and validates evidence; `service.py` coordinates; `persistence.py` stores references; `report.py` renders; `cli.py` exposes the command. NetworkX MultiDiGraph supports graph queries with stable edge IDs.

The actual analyzer protocol is `CodeAnalyzer.analyze(snapshot: Snapshot) -> Graph`, with `name` and `version`. `Graph` contains repository metadata, nodes, edges, evidence, coverage, diagnostics and findings. Do not implement against the earlier speculative AnalysisRequest/AnalysisResult types.

Source identity is a content-manifest revision; Git metadata is not the authority. Exact bytes travel as base64 in the internal snapshot. Long-lived artifacts contain locations/hashes, not excerpts. The separate fixture oracle is never input to analysis.

## Scope and limits

AST call relationships describe supported syntax, not runtime reachability or value propagation. Endpoint dependencies are observed DEPENDS_ON declarations, not proof of authorization execution. Unknown scopes suppress findings and remain diagnostic. Process limits and sanitized environment do not isolate filesystem/network access at OS level.

Artifacts are uniquely staged and renamed, then their validated references and results are committed together in SQLite. A crash between rename and commit can leave orphan files; readers use committed references. Existing output symlink aliases are rejected, but concurrent hostile filesystem replacement is outside scope.

## Future architecture — proposed only

The broader three-layer thesis remains code structure + application architecture + security context. Joern/CodeQL/Semgrep adapters, data-flow facts, asset/identity models, a FastAPI service, React/Cytoscape.js frontend and a bounded runtime explainer are separate future increments. Joern remains NOT_ATTEMPTED rather than a failed adapter or required predecessor to AST.

LangGraph may replace linear coordination if measured state/concurrency requirements justify it. Provider integration must remain evidence-bounded and separately authorized. Neo4j, distributed workers, object storage, per-tenant services and runtime telemetry are not current requirements; revisit only against measured needs. No directories, interfaces or dependencies are promised by this roadmap.
