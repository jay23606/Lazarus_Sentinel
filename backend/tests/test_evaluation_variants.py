"""Predeclared independent synthetic evaluation; target modules are never imported."""

import json
from pathlib import Path

from lazarus_sentinel.analysis import analyze
from lazarus_sentinel.intake import load_snapshot, verify_snapshot
from lazarus_sentinel.rules import evaluate_authorization, validate_evidence_snapshot

ROOT = Path(__file__).parents[2] / "fixtures/evaluation_variants"


def test_predeclared_variant_paths_evidence_and_determinism():
    oracle = json.loads((ROOT / "oracle.json").read_text())
    target = ROOT / oracle["fixture"]
    snapshot = load_snapshot(target)
    assert "oracle.json" not in snapshot.files
    graph = analyze(snapshot)
    evaluate_authorization(graph, snapshot.policy)
    validate_evidence_snapshot(graph, snapshot)
    nodes = {node.id: node for node in graph.nodes}
    endpoints = {node.name: node for node in graph.nodes if node.type == "API_ENDPOINT"}
    assert set(endpoints) == set(oracle["endpoints"])
    assert [nodes[f.entry_node_id].name for f in graph.findings] == oracle["candidate_paths"]
    for finding in graph.findings:
        assert nodes[finding.path_node_ids[-1]].qualified_name == oracle["terminal_operation"]
        assert finding.confidence == "LOW" and finding.verification_status == "CANDIDATE"
    for label, dependencies in oracle["declarations"].items():
        assert endpoints[label].properties["dependencies"] == dependencies
    unknown = endpoints["GET /unknown"]
    assert unknown.id not in {f.entry_node_id for f in graph.findings}
    assert any(d.code == "NEEDS_CONTEXT" for d in graph.diagnostics)
    repeated = analyze(snapshot)
    evaluate_authorization(repeated, snapshot.policy)
    assert repeated.model_dump() == graph.model_dump()
    verify_snapshot(target, snapshot)


def test_readonly_inspector_reports_orphans_and_corruption_without_repair(tmp_path):
    import importlib.util

    from lazarus_sentinel.service import scan

    script = ROOT.parents[1] / "scripts/inspect_artifacts.py"
    spec = importlib.util.spec_from_file_location("inspect_artifacts", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = scan("fixture:fastapi-demo", tmp_path)
    assert result["status"] == "PARTIAL"
    database = tmp_path / "sentinel.sqlite3"
    before = database.read_bytes()
    assert module.inspect(tmp_path)["status"] == "OK"
    orphan = tmp_path / "scans/00000000-0000-0000-0000-000000000000"
    orphan.mkdir()
    graph = tmp_path / result["artifact_dir"] / "graph.json"
    graph.write_bytes(graph.read_bytes() + b" ")
    report = module.inspect(tmp_path)
    assert {issue["code"] for issue in report["issues"]} == {
        "ARTIFACT_INVALID",
        "ORPHAN_OR_UNCOMMITTED_DIRECTORY",
    }
    assert database.read_bytes() == before
    assert orphan.is_dir() and graph.read_bytes().endswith(b" ")
