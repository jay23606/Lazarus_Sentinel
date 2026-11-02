"""Prepare one verified fixed-fixture demo. No live calls or arbitrary target paths."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend" / "src"))

from lazarus_sentinel.bundle import (
    export_json_schemas,
    load_committed_graph,
    parse_json,
    read_bounded,
    validate_bundle,
)


def cli(*args: str, expected: int = 0) -> dict:
    result = subprocess.run(
        [sys.executable, "-m", "lazarus_sentinel", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != expected:
        raise ValueError("DEMO_COMMAND_FAILED")
    return json.loads(result.stdout)


def prepare() -> dict:
    budget = ROOT / "artifacts" / "model-budget.sqlite3"
    budget_before = budget.read_bytes() if budget.exists() else None
    scan = cli("scan", "--target", "fixture:fastapi-demo", expected=2)
    loaded = load_committed_graph(scan["scan_id"])
    finding = next(f for f in loaded.graph.findings if f.confidence == "LOW")
    disabled = cli("explain", "--scan-id", scan["scan_id"], "--finding-id", finding.id)
    if disabled != {"status": "DISABLED", "provider": "disabled"}:
        raise ValueError("INVALID_DISABLED_RESULT")
    annotation = cli(
        "explain",
        "--scan-id",
        scan["scan_id"],
        "--finding-id",
        finding.id,
        "--provider",
        "mock",
    )
    exported = cli(
        "demo",
        "export",
        "--scan-id",
        scan["scan_id"],
        "--annotation-id",
        annotation["annotation_id"],
    )
    budget_after = budget.read_bytes() if budget.exists() else None
    if budget_after != budget_before:
        raise ValueError("MOCK_MODIFIED_LIVE_BUDGET")
    if load_committed_graph(scan["scan_id"]).graph_bytes != loaded.graph_bytes:
        raise ValueError("CANONICAL_GRAPH_CHANGED")
    source = ROOT / exported["artifact_dir"]
    manifest_bytes = read_bounded(source / "bundle.json")
    manifest = parse_json(manifest_bytes)
    payloads = {name: read_bounded(source / name) for name in manifest["artifacts"]}
    validate_bundle(manifest, payloads)
    if payloads["graph.json"] != loaded.graph_bytes:
        raise ValueError("GRAPH_BYTES_CHANGED")
    destination = ROOT / "frontend" / "public" / "demo" / "v1"
    destination.mkdir(parents=True, exist_ok=True)
    # Only fixed reviewed bundle filenames are ever copied into the viewer.
    for name, data in {"bundle.json": manifest_bytes, **payloads}.items():
        (destination / name).write_bytes(data)
    schemas = ROOT / "frontend" / "src" / "schemas"
    schemas.mkdir(parents=True, exist_ok=True)
    for name, schema in export_json_schemas().items():
        (schemas / name).write_text(json.dumps(schema, sort_keys=True, indent=2) + "\n")
    return {
        **exported,
        "annotation_id": annotation["annotation_id"],
        "finding_id": finding.id,
        "viewer_bundle": str(destination),
        "provider": "mock",
    }


if __name__ == "__main__":
    try:
        print(json.dumps(prepare(), sort_keys=True))
    except Exception:  # noqa: BLE001 - preparation must not echo target/provider exception text.
        print(
            json.dumps(
                {"status": "FAILED", "diagnostic_codes": ["DEMO_PREPARATION_FAILED"]}
            )
        )
        raise SystemExit(1) from None
