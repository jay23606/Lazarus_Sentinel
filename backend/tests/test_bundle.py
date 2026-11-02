import pytest

from lazarus_sentinel.bundle import validate_bundle


def test_invalid_bundle_rejected():
    with pytest.raises(ValueError):
        validate_bundle({}, {})


import hashlib
import json
import shutil
import sqlite3

from lazarus_sentinel import bundle, explanations, service
from lazarus_sentinel.bundle import export_demo_bundle, load_committed_graph


@pytest.fixture
def committed_scan(tmp_path, monkeypatch):
    shutil.copytree(service.FIXTURE_ROOT, tmp_path / "fixtures" / "fastapi_demo")
    for module in (bundle, explanations, service):
        monkeypatch.setattr(module, "WORKSPACE", tmp_path)
    result = service.scan("fixture:fastapi-demo", tmp_path / "artifacts")
    assert result["status"] == "PARTIAL"
    return tmp_path, result["scan_id"]


def test_export_is_fresh_exact_and_readonly(committed_scan):
    root, scan_id = committed_scan
    originals = {
        p: p.read_bytes() for p in (root / "artifacts" / "scans").rglob("*") if p.is_file()
    }
    loaded = load_committed_graph(scan_id)
    first = export_demo_bundle(scan_id)
    second = export_demo_bundle(scan_id)
    assert first["bundle_id"] != second["bundle_id"]
    directory = root / first["artifact_dir"]
    assert {p.name for p in directory.iterdir()} == {"bundle.json", "graph.json"}
    assert (directory / "graph.json").read_bytes() == loaded.graph_bytes
    manifest = json.loads((directory / "bundle.json").read_bytes())
    assert validate_bundle(manifest, {"graph.json": loaded.graph_bytes}) == loaded.graph
    assert all(p.read_bytes() == data for p, data in originals.items())


@pytest.mark.parametrize(
    "kind", ["hash", "path", "summary", "findings", "coverage", "symlink", "source"]
)
def test_committed_tampering_rejected(committed_scan, kind):
    root, scan_id = committed_scan
    artifact = root / "artifacts"
    with sqlite3.connect(artifact / "sentinel.sqlite3") as db:
        if kind == "hash":
            db.execute("UPDATE artifact_refs SET sha256=? WHERE kind='graph.json'", ("0" * 64,))
        elif kind == "path":
            db.execute("UPDATE artifact_refs SET path='../graph.json' WHERE kind='graph.json'")
        elif kind == "summary":
            row = db.execute("SELECT summary FROM scans").fetchone()
            summary = json.loads(row[0])
            summary["counts"]["nodes"] += 1
            db.execute("UPDATE scans SET summary=?", (json.dumps(summary),))
        elif kind in {"findings", "coverage"}:
            path = artifact / "scans" / scan_id / (kind + ".json")
            data = b"{}"
            path.write_bytes(data)
            db.execute(
                "UPDATE artifact_refs SET sha256=?,size=? WHERE kind=?",
                (hashlib.sha256(data).hexdigest(), len(data), path.name),
            )
        elif kind == "symlink":
            path = artifact / "scans" / scan_id / "graph.json"
            outside = root / "outside"
            path.rename(outside)
            path.symlink_to(outside)
        else:
            path = root / "fixtures" / "fastapi_demo" / "app" / "main.py"
            path.write_bytes(path.read_bytes() + b"\n# changed\n")
    with pytest.raises((ValueError, OSError, bundle.intake.ScanError)):
        load_committed_graph(scan_id)


@pytest.mark.parametrize(
    "mutation", ["version", "revision", "duplicate", "path", "cap", "hash", "unknownfile"]
)
def test_bundle_semantics_reject_mutation(committed_scan, mutation):
    root, scan_id = committed_scan
    exported = export_demo_bundle(scan_id)
    directory = root / exported["artifact_dir"]
    manifest = json.loads((directory / "bundle.json").read_bytes())
    graph = json.loads((directory / "graph.json").read_bytes())
    if mutation == "version":
        manifest["bundle_version"] = "9"
    elif mutation == "revision":
        manifest["scan"]["revision"] = "revision:sha256:" + "0" * 64
    elif mutation == "duplicate":
        graph["findings"].append(graph["findings"][0])
    elif mutation == "path":
        graph["findings"][0]["path_edge_ids"] = []
    elif mutation == "cap":
        graph["nodes"] *= 100
    payload = json.dumps(graph).encode()
    manifest["artifacts"]["graph.json"] = {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "size": len(payload),
    }
    payloads = {"graph.json": payload}
    if mutation == "hash":
        payloads["graph.json"] = payload + b" "
    if mutation == "unknownfile":
        payloads["unexpected"] = b"x"
    with pytest.raises(ValueError):
        validate_bundle(manifest, payloads)


def test_reader_missing_database_does_not_create(tmp_path, monkeypatch):
    monkeypatch.setattr(bundle, "WORKSPACE", tmp_path)
    with pytest.raises(sqlite3.OperationalError):
        load_committed_graph("00000000-0000-4000-8000-000000000000")
    assert list(tmp_path.iterdir()) == []


def test_bundle_required_metadata_and_total_limit(committed_scan):
    root, scan_id = committed_scan
    result = export_demo_bundle(scan_id)
    manifest = json.loads((root / result["artifact_dir"] / "bundle.json").read_bytes())
    data = load_committed_graph(scan_id).graph_bytes
    for field in ("bundle_version", "origin", "generator_version"):
        changed = dict(manifest)
        del changed[field]
        with pytest.raises(ValueError):
            validate_bundle(changed, {"graph.json": data})
    with pytest.raises(ValueError, match="BUNDLE_SIZE_LIMIT"):
        validate_bundle(manifest, {"graph.json": b" " * 1048576})
