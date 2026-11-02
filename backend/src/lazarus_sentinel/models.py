"""Versioned, analyzer-neutral artifact contracts. Source snippets are never retained."""

from __future__ import annotations

import base64
import hashlib
import json
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

FactStatus = Literal[
    "OBSERVED", "INFERRED", "UNKNOWN", "UNRESOLVED", "UNSUPPORTED", "HUMAN_ASSERTED"
]
Confidence = Literal["HIGH", "MEDIUM", "LOW"]
Severity = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
Layer = Literal["CODE", "APP", "SECURITY"]


def stable_id(kind: str, *parts: Any) -> str:
    payload = json.dumps(parts, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return f"{kind}:sha256:{hashlib.sha256(payload.encode()).hexdigest()}"


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Node(Model):
    schema_version: Literal["0.1.0"] = "0.1.0"
    id: str
    type: str
    layer: Layer
    name: str
    qualified_name: str = ""
    properties: dict[str, Any] = Field(default_factory=dict)
    fact_status: FactStatus = "OBSERVED"
    confidence: Confidence = "HIGH"
    evidence_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class Edge(Model):
    id: str
    source: str
    target: str
    type: str
    layer: Layer = "CODE"
    properties: dict[str, Any] = Field(default_factory=dict)
    fact_status: FactStatus = "OBSERVED"
    confidence: Confidence = "HIGH"
    evidence_ids: list[str] = Field(default_factory=list)
    analyzer: dict[str, str] = Field(default_factory=dict)


class Evidence(Model):
    id: str
    repository_revision: str
    file_path: str
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    symbol: str = ""
    excerpt_hash: str
    analyzer_name: str = "python_ast"
    analyzer_version: str = "0.1.0"
    rule_or_query_id: str
    evidence_kind: str
    created_at: str = ""

    @model_validator(mode="after")
    def ordered_range(self) -> Evidence:
        if self.end_line < self.start_line:
            raise ValueError("invalid evidence range")
        return self


class Coverage(Model):
    file_path: str
    status: Literal[
        "ANALYZED",
        "PARTIALLY_ANALYZED",
        "SKIPPED_BY_POLICY",
        "UNSUPPORTED_LANGUAGE",
        "PARSER_ERROR",
        "TIMEOUT",
        "NOT_ATTEMPTED",
        "EXCLUDED_GENERATED_OR_VENDOR",
    ]
    reason: str = ""
    analyzer: str = "python_ast"
    analyzer_version: str = "0.1.0"
    affected_concepts: list[str] = Field(default_factory=list)


class Diagnostic(Model):
    code: str
    message: str
    file_path: str | None = None
    severity: Literal["INFO", "WARNING", "ERROR"] = "WARNING"


class ProtectedOperation(Model):
    operation: str
    required_authorization: str
    severity: Severity
    impact: str
    author: str
    created_at: str


class SecurityPolicy(Model):
    protected_operations: list[ProtectedOperation]


class Snapshot(Model):
    revision: str
    root_label: str = "fastapi-demo"
    files: dict[str, str]
    file_hashes: dict[str, str]
    manifest_base64: str
    policy_base64: str
    policy_hash: str
    policy: SecurityPolicy


def source_bytes(snapshot: Snapshot, path: str) -> bytes:
    return base64.b64decode(snapshot.files[path], validate=True)


class Finding(Model):
    schema_version: Literal["0.1.0"] = "0.1.0"
    id: str
    rule_id: str = "LS-AUTH-001"
    rule_version: str = "0.1.0"
    title: str
    category: str = "BROKEN_ACCESS_CONTROL"
    severity: Severity
    confidence: Confidence = "LOW"
    verification_status: Literal["CANDIDATE"] = "CANDIDATE"
    triage_status: Literal["NEEDS_REVIEW"] = "NEEDS_REVIEW"
    assessment: Literal["POTENTIAL_GAP"] = "POTENTIAL_GAP"
    repository_revision: str
    entry_node_id: str
    path_node_ids: list[str]
    path_edge_ids: list[str]
    evidence_ids: list[str]
    impact_hypothesis: str = ""
    why_flagged: str = ""
    recognized_controls: list[str] = Field(default_factory=list)
    missing_or_uncertain_controls: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    false_positive_considerations: list[str] = Field(default_factory=list)
    human_review_steps: list[str] = Field(default_factory=list)
    coverage_context: dict[str, Any] = Field(default_factory=dict)
    created_at: str = ""


class Graph(Model):
    schema_version: Literal["0.1.0"] = "0.1.0"
    repository: dict[str, str]
    nodes: list[Node] = Field(default_factory=list)
    edges: list[Edge] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    coverage: list[Coverage] = Field(default_factory=list)
    diagnostics: list[Diagnostic] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)


class CodeAnalyzer(Protocol):
    name: str
    version: str

    def analyze(self, snapshot: Snapshot) -> Graph: ...
