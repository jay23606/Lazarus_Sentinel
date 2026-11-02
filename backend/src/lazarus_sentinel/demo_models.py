"""Strict, versioned boundaries for immutable demo exports and assistance."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Hex = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
Text = Annotated[str, StringConstraints(min_length=1, max_length=2000, strip_whitespace=True)]
Limit = Annotated[str, StringConstraints(min_length=1, max_length=500, strip_whitespace=True)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class ArtifactDigest(StrictModel):
    sha256: Hex
    size: int = Field(ge=1, le=1048576)


class DemoScan(StrictModel):
    scan_id: str
    revision: Annotated[str, StringConstraints(pattern=r"^revision:sha256:[0-9a-f]{64}$")]
    status: Literal["PARTIAL", "COMPLETED"]
    profile: Literal["reduced-static-auth"]

    @model_validator(mode="after")
    def uuid_id(self) -> DemoScan:
        if str(UUID(self.scan_id)) != self.scan_id:
            raise ValueError("INVALID_UUID")
        return self


class BundleManifest(StrictModel):
    bundle_version: Literal["0.1.0"]
    bundle_id: str
    origin: Literal["controlled-synthetic-fixture"]
    generator_version: Literal["0.1.0"]
    scan: DemoScan
    artifacts: dict[str, ArtifactDigest]

    @model_validator(mode="after")
    def exact_files(self) -> BundleManifest:
        if str(UUID(self.bundle_id)) != self.bundle_id:
            raise ValueError("INVALID_UUID")
        if set(self.artifacts) not in ({"graph.json"}, {"graph.json", "explanations.json"}):
            raise ValueError("INVALID_BUNDLE_FILES")
        return self


class ExplanationResponse(StrictModel):
    summary: Text
    why_it_matters: Text
    limitations: list[Limit] = Field(min_length=1, max_length=8)
    evidence_ids: list[str] = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def unique_citations(self) -> ExplanationResponse:
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError("DUPLICATE_CITATIONS")
        return self


class Annotation(StrictModel):
    annotation_version: Literal["0.1.0"]
    annotation_id: str
    scan_id: str
    revision: str
    graph_sha256: Hex
    finding_id: str
    request_sha256: Hex
    provider: Literal["mock", "meta"]
    model: Literal["deterministic-mock-v1", "muse-spark-1.3"]
    generation: Literal["mock", "live"]
    display_provenance: Literal["recorded"]
    review_status: Literal["UNREVIEWED"]
    created_at: str
    response: ExplanationResponse

    @model_validator(mode="after")
    def identities(self) -> Annotation:
        for value in (self.annotation_id, self.scan_id):
            if str(UUID(value)) != value:
                raise ValueError("INVALID_UUID")
        if (self.provider, self.model, self.generation) not in (
            ("mock", "deterministic-mock-v1", "mock"),
            ("meta", "muse-spark-1.3", "live"),
        ):
            raise ValueError("PROVENANCE_MISMATCH")
        if datetime.fromisoformat(self.created_at).utcoffset() != timedelta(0):
            raise ValueError("INVALID_TIMESTAMP")
        return self


class ExplanationEnvelope(StrictModel):
    annotation_version: Literal["0.1.0"]
    annotations: list[Annotation] = Field(min_length=1, max_length=1)


def export_json_schemas() -> dict[str, dict[str, Any]]:
    from .models import Graph

    return {
        "bundle.schema.json": BundleManifest.model_json_schema(),
        "graph.schema.json": Graph.model_json_schema(),
        "explanations.schema.json": ExplanationEnvelope.model_json_schema(),
    }
