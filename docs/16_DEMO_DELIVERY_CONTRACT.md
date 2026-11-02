# 16 — Approved integrated demo contract

Owner approved the parallel delivery plan on 2026-11-02. Preserve document 13's fixture analyzer. This increment adds validated immutable exports, recorded explanation sidecars and a fixed synthetic artifact viewer. Root coordinates; Sol owns backend, Terra frontend, independent QA owns evaluation; one Sol integration worker wires components after handoff. Astra reviews critical boundaries.

## Bundle v0.1.0 (frozen interface)

`lazarus demo export --scan-id <UUID> [--annotation-id <UUID>]` writes a NEW `artifacts/demo-bundles/<bundle_id>/` containing `bundle.json`, exact `graph.json` bytes, and optional `explanations.json`. No caller filesystem paths. Database is opened read-only, never via the mutating Store constructor. Validate exactly four committed original artifact refs, bounded reads/hashes, mirror agreement with graph/summary, graph semantics and current controlled source snapshot. Reject stale/unverifiable evidence. Preserve all original scans.

Manifest shape:

```json
{
  "bundle_version": "0.1.0",
  "bundle_id": "UUID",
  "origin": "controlled-synthetic-fixture",
  "generator_version": "0.1.0",
  "scan": {"scan_id": "UUID", "revision": "revision:sha256:...", "status": "PARTIAL", "profile": "reduced-static-auth"},
  "artifacts": {"graph.json": {"sha256": "64 lowercase hex characters", "size": 123}}
}
```

`explanations.json` may be the only additional artifact entry; it has the same hash/size record. Unknown files/fields/versions are rejected. Hash exact UTF-8 FILE BYTES, not parsed/re-serialized data. Total manifest+payload bytes <=1 MiB, <=500 graph nodes and <=2000 edges. Graph schema 0.1.0 remains canonical, including its findings/coverage/diagnostics. Reject duplicate finding/node/edge/evidence IDs, dangling refs, mismatched revision and invalid ordered finding paths. Export emits generated JSON schemas from Pydantic for the frontend to ship; schemas have local refs only and are application resources, not optional remote inputs.

Export schema/models live in backend demo_models.py. Schema source of truth is backend; frontend loads shipped copies and does not fetch remote refs. The integrator copies ONE validated synthetic export into frontend/public/demo/v1/. No browser upload/arbitrary URL/path/API/key handling. Hashes prove consistency against reviewed manifest, not authenticity if both manifest and files are replaced.

## Explanation v0.1.0 (frozen interface)

`lazarus explain --scan-id <UUID> --finding-id <ID> --provider disabled|mock|meta` defaults disabled. Disabled produces a safe DISABLED result and makes no model call. Successful mock/meta calls write NEW `artifacts/explanations/<annotation_id>.json`, never rewrite graph/finding/scan files. Export selects at most one explicit annotation ID and wraps it as `{"annotation_version":"0.1.0","annotations":[...]}` in explanations.json.

Annotation fields: annotation_version=0.1.0, annotation_id UUID, scan_id UUID, revision, graph_sha256 (hex), finding_id, request_sha256 (hex), provider=mock|meta, model (deterministic-mock-v1 or muse-spark-1.3), generation=mock|live, display_provenance=recorded, review_status=UNREVIEWED, created_at UTC ISO string, response. Response has ONLY summary (nonempty <=2000 chars), why_it_matters (nonempty <=2000), limitations (1–8 nonempty strings <=500 chars each), evidence_ids (1–64 unique allowed IDs). No authoritative field mutation, source snippets or unrelated graph/properties. Context/request hashing is deterministic: canonical JSON bytes (sorted keys, compact separators, ensure_ascii=True) of selected context plus prompt_version/provider/model; no credentials. Export recomputes request binding using the same pure builder.

Context is one validated finding's ID/rule, ordered path node/edge labels and identities, selected evidence locations/hashes, assumptions and unknowns; <=16 KiB including fixed prompt/request framing. Response <=32 KiB while reading. Explain annotations retain existing canonical facts unchanged. Schema-valid prose is unverified assistance, not proof or human confirmation.

## Live transport and budget

Standard muse-spark-1.3 at https://api.meta.ai/v1/chat/completions, MODEL_API_KEY only; max_completion_tokens=1024, response_format JSON object/schema as supported by verified official protocol, no tools, streaming, redirects or retries. Enforce20-second absolute operation deadline including DNS/connection/read via a bounded child or equivalent killable execution. Do not log credentials, headers, provider error bodies or raw prompts. Key presence never enables provider meta implicitly.

USD3 and five live ATTEMPTS are shared across all invocations for this demo. Transactional local budget ledger reserves conservative cost BEFORE transport using verified uncached pricing, full request byte upper bound plus conservative framing allowance, output cap and a margin. Reserve at least USD0.10/call; refuse if prices/upper bound cannot be established. Keep reservations on ambiguous failures/crashes/missing usage and block more calls pending reconciliation. Only unambiguous returned usage settles reservation; counts never reset silently. This caps this application, not unrelated account spending. Missing key/access remains BLOCKED; mock remains distinct. No key currently configured; do not search secret files.

## Viewer and acceptance

React/Vite/TypeScript + Cytoscape, local pinned deps/lockfile. Neutral high-contrast workspace, blue selection and amber PARTIAL/unknown; non-color labels. Findings/endpoints list, graph, selected detail, evidence/path tables and coverage. Render exact graph path IDs and edge IDs, LOW confidence separately from severity, declarations effectiveness unverified, mock/live-recorded provenance. All text escaped; no unsafe HTML or unrestricted evidence URLs. Invalid data suppresses graph/success counts; display failure separate from original scan status.

Provide keyboard/table fallback, 320px layout and200% zoom checks. Tests: hashes/version/revisions/caps/duplicates/references/path/sidecar bindings; source/scan immutability; provider injection/timeout/budget concurrency; UI selection/error/escaped labels; clean build and browser desktop/mobile. Preserve73-test baseline and expected PARTIAL demo. Independent Astra review required before completion.

## Roadmap dispositions

N01 eligibility/submission facts require owner portal access. N02 live verification blocked absent key. N09 optional two-hour measured release-specific analyzer spike; no global installation. N10 DATA/TRUST only after real capability/policy gates; do not rename CALLS. N11 API skipped unless viewer needs it. N14 actual OS denial/resource probes before isolation approval; unavailable runner blocked. N15 waits for N14; N16 predeclared subsets; N17 artifact integrity/recovery inspection, reproducibility and credential-free CI; N18 catalog all topics and deeply evaluate DATA/TRUST first. Research is not detector implementation. No remote publication/deployment/submission implied.
