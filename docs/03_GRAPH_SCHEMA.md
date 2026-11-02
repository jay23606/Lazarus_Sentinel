# 03 — Normalized Graph Schema and Evidence Model

Current schema is implemented in `backend/src/lazarus_sentinel/models.py` and governed by the [first-slice contract](13_FIRST_SLICE_CONTRACT.md). The vocabulary below includes future concepts; it is not a claim that the analyzer emits every type. See [verified results](14_IMPLEMENTATION_REVIEW.md) and [proposed next steps](15_NEXT_STEPS.md).

## 1. Design goals

- Analyzer-neutral representation.
- Clear separation between facts, inferences, and unknowns.
- Source provenance for every source-derived node and edge.
- Stable identities within a repository revision.
- Versioned schema.
- Support for code, application architecture, and security context.
- No claim that static analysis yields the complete runtime graph.

Set `schema_version` on every graph artifact and finding export.

## 2. Node model

Implemented node envelope (illustrative values):

```json
{
  "schema_version": "0.1.0",
  "id": "node:sha256:...",
  "type": "FUNCTION",
  "layer": "CODE",
  "name": "get_profile",
  "qualified_name": "app.services.profile.get_profile",
  "properties": {},
  "fact_status": "OBSERVED",
  "confidence": "HIGH",
  "evidence_ids": ["ev_0001"],
  "tags": ["application_logic"]
}
```

### Vocabulary roadmap and emitted subset

The current adapter emits MODULE, CLASS, FUNCTION and API_ENDPOINT. Other types below are future vocabulary, not extracted capabilities.

| Type | Layer | Meaning |
|---|---|---|
| `PROJECT` | APP | Repository/project root |
| `PACKAGE` | CODE | Package or namespace |
| `MODULE` | CODE | Source module/file |
| `CLASS` | CODE | Class/type |
| `FUNCTION` | CODE | Function or method |
| `VARIABLE` | CODE | Variable/parameter where supported |
| `API_ENDPOINT` | APP | Exposed route/operation |
| `SERVICE` | APP | Business/application service |
| `REPOSITORY` | APP | Data-access component |
| `DATABASE` | APP | Data store |
| `EXTERNAL_SERVICE` | APP | Remote API/service |
| `MESSAGE_QUEUE` | APP | Queue/topic/event transport |
| `USER_IDENTITY` | SECURITY | User/service identity concept |
| `ROLE` | SECURITY | Role/group concept |
| `PERMISSION` | SECURITY | Permission/action scope |
| `DATA_ASSET` | SECURITY | Data class/asset |
| `TRUST_BOUNDARY` | SECURITY | Change in trust/security context |
| `SECURITY_CONTROL` | SECURITY | Authentication, authorization, validation, encoding, etc. |
| `SOURCE` | SECURITY | Untrusted or classified input origin |
| `SINK` | SECURITY | Sensitive operation/data destination |
| `DEPENDENCY` | APP | Third-party package/component |
| `CONFIGURATION` | APP | Security-relevant config item |

Do not create a new node type for every framework concept. Prefer a stable type plus typed properties until a real query requirement justifies a new type.

## 3. Edge model

Implemented edge envelope (illustrative values):

```json
{
  "id": "edge:sha256:...",
  "source": "node:...",
  "target": "node:...",
  "type": "CALLS",
  "layer": "CODE",
  "properties": {},
  "fact_status": "OBSERVED",
  "confidence": "HIGH",
  "evidence_ids": ["ev_0002"],
  "analyzer": {"name": "python_ast", "version": "0.1.0"}
}
```

### Vocabulary roadmap and emitted subset

Current edges are CONTAINS, IMPORTS, CALLS, HANDLES and DEPENDS_ON. DEPENDS_ON records explicit function dependency declarations, not effective authorization. FLOWS_TO, AUTHORIZES, GUARDED_BY and other entries below are future vocabulary. Unknown control scopes produce diagnostics rather than security findings.

- `CONTAINS`
- `IMPORTS`
- `CALLS`
- `READS`
- `WRITES`
- `DEFINES`
- `REFERENCES`
- `FLOWS_TO`
- `EXPOSES`
- `HANDLES`
- `ACCESSES`
- `DEPENDS_ON`
- `GUARDED_BY`
- `AUTHENTICATES`
- `AUTHORIZES`
- `VALIDATED_BY`
- `SANITIZED_BY`
- `CROSSES`
- `LOGS_TO`
- `SENDS_TO`
- `STORES_IN`
- `HAS_ROLE`
- `HAS_PERMISSION`
- `OWNS`
- `POSSIBLY_SAME_AS` (only when explicitly uncertain and supported by evidence)

Do not create `GUARDED_BY` simply because an LLM says a dependency name looks like auth. Require a recognized extractor/rule or human assertion with explicit provenance.

## 4. Fact status and uncertainty

Use a controlled enum:

- `OBSERVED`: directly supported by parser/analyzer/source construct.
- `INFERRED`: inferred through a documented rule or model-assisted hypothesis.
- `UNKNOWN`: insufficient information.
- `UNRESOLVED`: analysis found a relationship but could not resolve its destination/semantics.
- `UNSUPPORTED`: construct/tool/framework behavior is outside supported analysis.
- `HUMAN_ASSERTED`: supplied by a human, with actor and timestamp.

Do not overload confidence with fact status. `OBSERVED` is not identical to “secure”; it only describes the source of the fact.

## 5. Evidence model

Every source-derived fact must point to one or more evidence records:

```json
{
  "id": "ev_0001",
  "repository_revision": "git-sha-or-content-manifest",
  "file_path": "app/routes/profile.py",
  "start_line": 18,
  "end_line": 31,
  "symbol": "get_profile",
  "excerpt_hash": "sha256:...",
  "analyzer_name": "python_ast",
  "analyzer_version": "...",
  "rule_or_query_id": "fastapi.route.extract.v1",
  "evidence_kind": "AST_DECORATOR",
  "created_at": "ISO-8601 timestamp"
}
```

The implemented Evidence model forbids extra fields, including excerpt_redacted. It retains exact byte-range hashes and relative source locations, never source snippets. No external model calls are enabled; any future egress needs separately approved minimization/redaction. The current revision is a content-manifest hash including policy; no Git repository was initialized.

## 6. Stable IDs

Use deterministic IDs derived from a canonical tuple, such as:

- repository revision;
- node/edge type;
- normalized relative file path;
- qualified symbol name;
- source range or stable parser-specific ID.

Do not use only symbol names: duplicate function names and overloaded methods exist. Do not include absolute host paths in externally visible IDs.

## 7. Graph layers

### Layer A — Code structure

Implemented: modules, functions/classes, membership/imports and unambiguous direct calls. CPG, control-flow and data-flow extraction are future capabilities.

### Layer B — Application architecture

Implemented: supported literal routes, handlers and explicit dependency declarations. Service/storage/queue/external-system semantics are future enrichment.

### Layer C — Security context

Implemented: operator policy and declaration-context assessments with explicit unknowns. Identity/role/asset/trust-boundary graph enrichment remains future work.

Cross-layer edges should preserve their source. For example, `API_ENDPOINT --HANDLES--> FUNCTION` comes from a framework route extractor, while `FUNCTION --CALLS--> FUNCTION` comes from a program analyzer.

## 8. Coverage model

Coverage must be explicit, ideally by file, language, framework, feature and analysis pass.

Suggested coverage statuses:

- `ANALYZED`
- `PARTIALLY_ANALYZED`
- `SKIPPED_BY_POLICY`
- `UNSUPPORTED_LANGUAGE`
- `PARSER_ERROR`
- `TIMEOUT`
- `NOT_ATTEMPTED`
- `EXCLUDED_GENERATED_OR_VENDOR`

Implemented Coverage fields are file_path, status, reason, analyzer, analyzer_version and affected_concepts. Diagnostic records separately contain code, message, optional file_path and severity. Per-pass timing and source-range coverage are not current fields.

## 9. Graph artifact format

Portable output:

```json
{
  "schema_version": "0.1.0",
  "repository": {"revision": "...", "root_label": "project"},
  "nodes": [],
  "edges": [],
  "evidence": [],
  "coverage": [],
  "diagnostics": [],
  "findings": []
}
```

Current artifacts are JSON; JSONL would be a future storage choice. The canonical serialized format must not depend on Python pickle or an in-memory NetworkX object.

## 10. Finding linkage

A finding references:

- the rule ID/version;
- one or more graph node IDs and edge IDs;
- one or more evidence IDs;
- the relevant repository revision;
- uncertainty/assumptions;
- any human triage status.

If a line range cannot be mapped back to the exact scanned revision, the finding is incomplete and should not be shown as a verified source-level result.

## 11. Implemented finding contract

Findings carry schema/rule version 0.1.0 and fixed verification_status=CANDIDATE, triage_status=NEEDS_REVIEW and assessment=POTENTIAL_GAP. Confidence is LOW for current LS-AUTH-001 output; severity is the operator policy impact assumption. Path node/edge IDs, evidence IDs, assumptions, unknowns and human-review guidance are retained. NEEDS_CONTEXT belongs to diagnostics; there is no editable triage subsystem or confirmed finding state. Graph includes its findings array in addition to the separate findings.json export. Pydantic models reject extra fields.
