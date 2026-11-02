"""Read-only committed scan verification and immutable synthetic demo export."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from . import intake
from .demo_models import (
    ArtifactDigest,
    BundleManifest,
    DemoScan,
    ExplanationEnvelope,
    export_json_schemas,
)
from .models import Graph
from .rules import validate_evidence_snapshot, validate_graph
from .service import WORKSPACE

MAX_BYTES = 1048576
ORIGINAL_FILES = {"graph.json", "findings.json", "coverage.json", "report.md"}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checked_uuid(value: str) -> str:
    if str(UUID(value)) != value:
        raise ValueError("INVALID_UUID")
    return value


def read_bounded(path: Path, limit: int = MAX_BYTES) -> bytes:
    intake.reject_symlink_components(path)
    if not path.is_file() or path.stat().st_size > limit:
        raise ValueError("INVALID_ARTIFACT_SIZE")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError("INVALID_ARTIFACT_SIZE")
    return data


def parse_json(data: bytes) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("DUPLICATE_JSON_KEYS")
            result[key] = value
        return result

    def reject(value: str) -> None:
        raise ValueError("INVALID_JSON_CONSTANT")

    return json.loads(data.decode("utf-8"), object_pairs_hook=pairs, parse_constant=reject)


def validate_demo_graph(graph: Graph) -> None:
    validate_graph(graph)
    if len(graph.nodes) > 500 or len(graph.edges) > 2000:
        raise ValueError("GRAPH_LIMIT")
    if len({f.id for f in graph.findings}) != len(graph.findings):
        raise ValueError("DUPLICATE_FINDING_IDS")


@dataclass(frozen=True)
class LoadedScan:
    summary: dict[str, Any]
    graph: Graph
    graph_bytes: bytes
    graph_sha256: str


def load_committed_graph(scan_id: str) -> LoadedScan:
    checked_uuid(scan_id)
    root = WORKSPACE / "artifacts"
    db_path = root / "sentinel.sqlite3"
    for suffix in ("", "-journal", "-wal", "-shm"):
        intake.reject_symlink_components(Path(str(db_path) + suffix))
    with sqlite3.connect(db_path.as_uri() + "?mode=ro", uri=True) as db:
        db.execute("PRAGMA query_only=ON")
        row = db.execute("SELECT status,summary FROM scans WHERE scan_id=?", (scan_id,)).fetchone()
        if row is None or row[0] not in {"PARTIAL", "COMPLETED"}:
            raise ValueError("SCAN_NOT_COMMITTED")
        summary = parse_json(row[1].encode())
        refs = db.execute(
            "SELECT kind,path,sha256,size FROM artifact_refs WHERE scan_id=?", (scan_id,)
        ).fetchall()
        findings = [
            parse_json(r[0].encode())
            for r in db.execute(
                "SELECT body FROM findings WHERE scan_id=? ORDER BY finding_id", (scan_id,)
            )
        ]
    if len(refs) != 4 or {r[0] for r in refs} != ORIGINAL_FILES:
        raise ValueError("INVALID_COMMITTED_REFERENCES")
    payloads = {}
    for kind, path, sha, size in refs:
        if path != f"scans/{scan_id}/{kind}" or type(size) is not int or not 0 < size <= MAX_BYTES:
            raise ValueError("INVALID_COMMITTED_REFERENCE")
        data = read_bounded(root / path)
        if len(data) != size or digest(data) != sha:
            raise ValueError("ARTIFACT_HASH_MISMATCH")
        payloads[kind] = data
    graph = Graph.model_validate(parse_json(payloads["graph.json"]))
    validate_demo_graph(graph)
    expected_findings = [f.model_dump(mode="json") for f in graph.findings]
    if (
        parse_json(payloads["findings.json"])
        != {"schema_version": "0.1.0", "findings": expected_findings}
        or sorted(findings, key=lambda f: f["id"])
        != sorted(expected_findings, key=lambda f: f["id"])
        or parse_json(payloads["coverage.json"])
        != {
            "schema_version": "0.1.0",
            "coverage": [c.model_dump(mode="json") for c in graph.coverage],
            "diagnostics": [d.model_dump(mode="json") for d in graph.diagnostics],
        }
    ):
        raise ValueError("ARTIFACT_MIRROR_MISMATCH")
    partial = any(
        c.status in {"PARTIALLY_ANALYZED", "UNSUPPORTED_LANGUAGE", "PARSER_ERROR", "TIMEOUT"}
        for c in graph.coverage
    )
    if (
        summary.get("scan_id") != scan_id
        or summary.get("status") != row[0]
        or row[0] != ("PARTIAL" if partial else "COMPLETED")
        or summary.get("revision") != graph.repository.get("revision")
        or summary.get("profile") != "reduced-static-auth"
        or summary.get("counts")
        != {"nodes": len(graph.nodes), "edges": len(graph.edges), "findings": len(graph.findings)}
        or summary.get("schema_version") != "0.1.0"
        or summary.get("artifact_dir") != f"artifacts/scans/{scan_id}"
        or summary.get("diagnostic_codes") != sorted({d.code for d in graph.diagnostics})
    ):
        raise ValueError("SUMMARY_MIRROR_MISMATCH")
    snapshot = intake.load_snapshot(WORKSPACE / "fixtures" / "fastapi_demo")
    validate_evidence_snapshot(graph, snapshot)
    return LoadedScan(summary, graph, payloads["graph.json"], digest(payloads["graph.json"]))


def validate_bundle(manifest: dict[str, Any], payloads: dict[str, bytes]) -> Graph:
    parsed = BundleManifest.model_validate(manifest)
    if set(payloads) != set(parsed.artifacts):
        raise ValueError("BUNDLE_FILES_MISMATCH")
    if len(canonical_bytes(manifest)) + sum(map(len, payloads.values())) > MAX_BYTES:
        raise ValueError("BUNDLE_SIZE_LIMIT")
    for name, record in parsed.artifacts.items():
        if len(payloads[name]) != record.size or digest(payloads[name]) != record.sha256:
            raise ValueError("BUNDLE_HASH_MISMATCH")
    graph = Graph.model_validate(parse_json(payloads["graph.json"]))
    validate_demo_graph(graph)
    if graph.repository.get("revision") != parsed.scan.revision:
        raise ValueError("BUNDLE_REVISION_MISMATCH")
    partial = any(
        c.status in {"PARTIALLY_ANALYZED", "UNSUPPORTED_LANGUAGE", "PARSER_ERROR", "TIMEOUT"}
        for c in graph.coverage
    )
    if parsed.scan.status != ("PARTIAL" if partial else "COMPLETED"):
        raise ValueError("BUNDLE_STATUS_MISMATCH")
    if "explanations.json" in payloads:
        from .explanations import validate_annotation

        envelope = ExplanationEnvelope.model_validate(parse_json(payloads["explanations.json"]))
        loaded = LoadedScan(
            parsed.scan.model_dump(), graph, payloads["graph.json"], digest(payloads["graph.json"])
        )
        for annotation in envelope.annotations:
            validate_annotation(annotation, loaded)
    return graph


def export_demo_bundle(scan_id: str, annotation_id: str | None = None) -> dict[str, Any]:
    loaded = load_committed_graph(scan_id)
    payloads = {"graph.json": loaded.graph_bytes}
    if annotation_id is not None:
        from .explanations import validate_annotation

        checked_uuid(annotation_id)
        annotation = validate_annotation(
            parse_json(
                read_bounded(
                    WORKSPACE / "artifacts" / "explanations" / f"{annotation_id}.json", 32768
                )
            ),
            loaded,
        )
        if annotation.annotation_id != annotation_id:
            raise ValueError("ANNOTATION_ID_MISMATCH")
        payloads["explanations.json"] = canonical_bytes(
            ExplanationEnvelope(annotation_version="0.1.0", annotations=[annotation]).model_dump(
                mode="json"
            )
        )
    bundle_id = str(uuid4())
    manifest = BundleManifest(
        bundle_version="0.1.0",
        origin="controlled-synthetic-fixture",
        generator_version="0.1.0",
        bundle_id=bundle_id,
        scan=DemoScan.model_validate(
            {k: loaded.summary[k] for k in ("scan_id", "revision", "status", "profile")}
        ),
        artifacts={
            name: ArtifactDigest(sha256=digest(data), size=len(data))
            for name, data in payloads.items()
        },
    ).model_dump(mode="json")
    validate_bundle(manifest, payloads)
    if load_committed_graph(scan_id).graph_sha256 != loaded.graph_sha256:
        raise ValueError("STALE_GRAPH")
    directory = WORKSPACE / "artifacts" / "demo-bundles"
    intake.reject_symlink_components(directory)
    directory.mkdir(mode=0o700, exist_ok=True)
    stage = directory / ("." + bundle_id + ".staging")
    stage.mkdir(mode=0o700)
    try:
        for name, data in {"bundle.json": canonical_bytes(manifest), **payloads}.items():
            with (stage / name).open("xb") as stream:
                stream.write(data)
        os.rename(stage, directory / bundle_id)
    except BaseException:
        import shutil

        shutil.rmtree(stage)
        raise
    return {
        "status": "EXPORTED",
        "bundle_id": bundle_id,
        "artifact_dir": f"artifacts/demo-bundles/{bundle_id}",
        "scan_id": scan_id,
    }


__all__ = [
    "LoadedScan",
    "export_demo_bundle",
    "export_json_schemas",
    "load_committed_graph",
    "validate_bundle",
]
