"""Fixture-only scan orchestration and atomic artifact publication."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from . import intake, worker
from .models import Coverage, Evidence, stable_id
from .persistence import Store
from .report import render_report
from .rules import evaluate_authorization, validate_evidence_snapshot

WORKSPACE = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = WORKSPACE / "fixtures" / "fastapi_demo"


def scan(target: str, artifact_root: Path | None = None) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "scan_id": str(uuid4()),
        "status": "FAILED",
        "artifact_dir": None,
        "counts": {},
        "diagnostic_codes": [],
        "schema_version": "0.1.0",
        "profile": "reduced-static-auth",
        "created_at": datetime.now(UTC).isoformat(),
    }
    if target != "fixture:fastapi-demo":
        summary["diagnostic_codes"] = ["INVALID_TARGET"]
        return summary
    root = artifact_root if artifact_root is not None else WORKSPACE / "artifacts"
    store = None
    stage = None
    try:
        store = Store(root)
        with store.writer():
            store.start(summary["scan_id"])
            try:
                snapshot = intake.load_snapshot(FIXTURE_ROOT)
                summary["revision"] = snapshot.revision
                graph = worker.analyze_snapshot(snapshot, timeout_seconds=30)
                policy_bytes = base64.b64decode(snapshot.policy_base64, validate=True)
                policy_id = stable_id(
                    "evidence", snapshot.revision, "policy.json", snapshot.policy_hash
                )
                graph.evidence.append(
                    Evidence(
                        id=policy_id,
                        repository_revision=snapshot.revision,
                        file_path="policy.json",
                        start_line=1,
                        end_line=max(1, len(policy_bytes.splitlines())),
                        symbol="protected_operations",
                        excerpt_hash="sha256:" + snapshot.policy_hash,
                        analyzer_name="human_policy",
                        rule_or_query_id="LS-AUTH-001",
                        evidence_kind="HUMAN_ASSERTION",
                    )
                )
                evaluate_authorization(graph, snapshot.policy)
                for finding in graph.findings:
                    finding.evidence_ids = sorted(set(finding.evidence_ids) | {policy_id})
                graph.coverage.extend(
                    [
                        Coverage(
                            file_path="", status="NOT_ATTEMPTED", analyzer=analyzer, reason=reason
                        )
                        for analyzer, reason in [
                            ("LS-DATA-001", "NOT_IMPLEMENTED"),
                            ("LS-TRUST-001", "NOT_IMPLEMENTED"),
                            ("joern", "NOT_ATTEMPTED"),
                        ]
                    ]
                )
                validate_evidence_snapshot(graph, snapshot)
                partial = any(
                    c.status
                    in {"PARTIALLY_ANALYZED", "UNSUPPORTED_LANGUAGE", "PARSER_ERROR", "TIMEOUT"}
                    for c in graph.coverage
                )
                summary.update(
                    status="PARTIAL" if partial else "COMPLETED",
                    counts={
                        "nodes": len(graph.nodes),
                        "edges": len(graph.edges),
                        "findings": len(graph.findings),
                    },
                    diagnostic_codes=sorted({d.code for d in graph.diagnostics}),
                )
                scans = root / "scans"
                intake.reject_symlink_components(scans)
                scans.mkdir(exist_ok=True, mode=0o700)
                stage = scans / ("." + summary["scan_id"] + ".staging")
                stage.mkdir(mode=0o700)
                payloads = {
                    "graph.json": graph.model_dump(mode="json"),
                    "findings.json": {
                        "schema_version": "0.1.0",
                        "findings": [f.model_dump(mode="json") for f in graph.findings],
                    },
                    "coverage.json": {
                        "schema_version": "0.1.0",
                        "coverage": [c.model_dump(mode="json") for c in graph.coverage],
                        "diagnostics": [d.model_dump(mode="json") for d in graph.diagnostics],
                    },
                }
                for name, payload in payloads.items():
                    (stage / name).write_text(
                        json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8"
                    )
                (stage / "report.md").write_text(
                    render_report(graph, summary["status"]), encoding="utf-8"
                )
                intake.verify_snapshot(FIXTURE_ROOT, snapshot)
                final = scans / summary["scan_id"]
                os.rename(stage, final)
                stage = None
                intake.verify_snapshot(FIXTURE_ROOT, snapshot)
                refs = []
                for file in sorted(final.iterdir()):
                    data = file.read_bytes()
                    refs.append(
                        (
                            file.name,
                            file.relative_to(root).as_posix(),
                            hashlib.sha256(data).hexdigest(),
                            len(data),
                        )
                    )
                summary["artifact_dir"] = (
                    final.relative_to(WORKSPACE).as_posix()
                    if final.is_relative_to(WORKSPACE)
                    else final.relative_to(root).as_posix()
                )
                summary["finished_at"] = datetime.now(UTC).isoformat()
                store.finish(summary, graph.findings, refs)
            except (intake.ScanError, OSError, ValueError, RuntimeError, sqlite3.Error):
                summary.update(
                    status="FAILED", artifact_dir=None, counts={}, diagnostic_codes=["SCAN_FAILED"]
                )
                summary["finished_at"] = datetime.now(UTC).isoformat()
                store.finish(summary)
    except (intake.ScanError, OSError, ValueError, RuntimeError, sqlite3.Error):
        summary.update(
            status="FAILED", artifact_dir=None, counts={}, diagnostic_codes=["STORAGE_FAILED"]
        )
    finally:
        if stage is not None:
            shutil.rmtree(stage, ignore_errors=True)
        if store is not None:
            store.close()
    return summary
