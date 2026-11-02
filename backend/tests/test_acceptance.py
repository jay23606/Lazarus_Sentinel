"""End-to-end acceptance against owned synthetic source; no target imports."""

import hashlib
import json
import socket
import urllib.request
from pathlib import Path
from unittest.mock import Mock

import networkx as nx
import pytest

from lazarus_sentinel import rules, service
from lazarus_sentinel.intake import ScanError, load_snapshot, verify_snapshot
from lazarus_sentinel.models import Graph
from lazarus_sentinel.persistence import Store
from lazarus_sentinel.worker import analyze_snapshot

ROOT = Path(__file__).resolve().parents[2]


def owned_fixture(root, source, protected_operations=None):
    root.mkdir()
    (root / "main.py").write_text(source)
    (root / "manifest.json").write_text(json.dumps(["main.py", "policy.json"]))
    (root / "policy.json").write_text(
        json.dumps({"protected_operations": protected_operations or []})
    )
    return root


def test_service_oracle_stability_and_persisted_content_hashes(tmp_path):
    oracle = json.loads((ROOT / "fixtures/expected_results/fastapi_demo.json").read_text())
    summaries = [service.scan("fixture:fastapi-demo", tmp_path) for _ in range(2)]
    graphs = []
    store = Store(tmp_path)
    try:
        for summary in summaries:
            assert summary["status"] == "PARTIAL"
            row = store.get(summary["scan_id"])
            assert row is not None
            assert {ref["kind"] for ref in row["artifacts"]} == {
                "graph.json",
                "findings.json",
                "coverage.json",
                "report.md",
            }
            for ref in row["artifacts"]:
                content = (tmp_path / ref["path"]).read_bytes()
                assert len(content) == ref["size"]
                assert hashlib.sha256(content).hexdigest() == ref["sha256"]
            graph = Graph.model_validate_json(
                (tmp_path / summary["artifact_dir"] / "graph.json").read_bytes()
            )
            rules.validate_evidence_snapshot(graph, load_snapshot(service.FIXTURE_ROOT))
            graphs.append(graph)
    finally:
        store.close()
    graph = graphs[0]
    endpoints = {node.id: node for node in graph.nodes if node.type == "API_ENDPOINT"}
    assert {node.name for node in endpoints.values()} == set(oracle["endpoints"])
    assert {endpoints[f.entry_node_id].name for f in graph.findings} == set(
        oracle["candidate_paths"]
    )
    required = "app.controls.authorize_export"
    assert {
        node.name for node in endpoints.values() if required in node.properties["dependencies"]
    } == set(oracle["recognized_authorization"])
    codes = {diagnostic.code for diagnostic in graph.diagnostics}
    assert {"NEEDS_CONTEXT", "AUTHORIZATION_DECLARATION_RECOGNIZED"} <= codes
    assert [n.id for n in graphs[0].nodes] == [n.id for n in graphs[1].nodes]
    assert [e.id for e in graphs[0].edges] == [e.id for e in graphs[1].edges]
    assert [e.evidence_ids for e in graphs[0].edges] == [e.evidence_ids for e in graphs[1].edges]


def test_parallel_calls_retain_distinct_evidence_in_rule_multigraph(tmp_path, monkeypatch):
    root = owned_fixture(
        tmp_path / "owned",
        """from fastapi import FastAPI
app = FastAPI()
def authorize(): pass
def sensitive(): pass
@app.get("/twice")
def handler():
    sensitive()
    sensitive()
""",
        [
            {
                "operation": "main.sensitive",
                "required_authorization": "main.authorize",
                "severity": "HIGH",
                "impact": "Synthetic data",
                "author": "fixture-owner",
                "created_at": "2026-11-01",
            }
        ],
    )
    snapshot = load_snapshot(root)
    graph = analyze_snapshot(snapshot)
    calls = [edge for edge in graph.edges if edge.type == "CALLS"]
    assert len(calls) == 2
    assert len({(edge.source, edge.target) for edge in calls}) == 1
    assert len({edge.id for edge in calls}) == 2
    assert len({tuple(edge.evidence_ids) for edge in calls}) == 2
    network = nx.MultiDiGraph()
    monkeypatch.setattr(rules.nx, "MultiDiGraph", lambda: network)
    rules.evaluate_authorization(graph, snapshot.policy)
    assert set(network[calls[0].source][calls[0].target]) == {edge.id for edge in calls}
    assert len(graph.findings) == 1
    assert graph.findings[0].path_edge_ids[-1] == min(edge.id for edge in calls)


def test_real_worker_never_imports_source_or_calls_network_and_report_retains_no_literals(
    tmp_path, monkeypatch
):
    sentinel = tmp_path / "executed"
    network_sentinel = tmp_path / "network-called"
    fake_token = "SYNTHETIC_SOURCE_SECRET_DO_NOT_RETAIN_879321"
    # If mistakenly imported, both side effects are observable without any real network request.
    source = f"""from pathlib import Path
import urllib.request
Path({str(sentinel)!r}).write_text("executed")
def fake_urlopen(*args):
    Path({str(network_sentinel)!r}).write_text("called")
urllib.request.urlopen = fake_urlopen
urllib.request.urlopen("https://example.invalid")
TOKEN = {fake_token!r}
def safe(): pass
"""
    root = owned_fixture(tmp_path / "owned", source)
    network_mock = Mock(side_effect=AssertionError("parent network attempted"))
    monkeypatch.setattr(socket, "create_connection", network_mock)
    monkeypatch.setattr(urllib.request, "urlopen", network_mock)
    snapshot = load_snapshot(root)
    monkeypatch.setattr(service, "FIXTURE_ROOT", root)
    artifact_root = tmp_path / "artifacts"
    result = service.scan("fixture:fastapi-demo", artifact_root)
    assert result["status"] in {"COMPLETED", "PARTIAL"}
    published = artifact_root / result["artifact_dir"]
    graph = Graph.model_validate_json((published / "graph.json").read_bytes())
    rules.validate_evidence_snapshot(graph, snapshot)
    report = (published / "report.md").read_text()
    assert all(fake_token not in artifact.read_text() for artifact in published.iterdir())
    assert not sentinel.exists()
    assert not network_sentinel.exists()
    network_mock.assert_not_called()
    assert fake_token not in graph.model_dump_json()
    assert fake_token not in report
    assert str(tmp_path) not in graph.model_dump_json()
    assert str(tmp_path) not in report


def test_manifest_and_policy_and_source_revision_invalidation(tmp_path):
    root = owned_fixture(tmp_path / "owned", "def safe(): pass\n")
    initial = load_snapshot(root)
    assert initial == load_snapshot(root)
    (root / "manifest.json").write_text('[ "main.py", "policy.json" ]')
    manifest_changed = load_snapshot(root)
    assert initial.revision != manifest_changed.revision
    (root / "policy.json").write_text('{ "protected_operations": [] }')
    policy_changed = load_snapshot(root)
    assert manifest_changed.revision != policy_changed.revision
    (root / "main.py").write_text("def safe(): return 1\n")
    source_changed = load_snapshot(root)
    assert source_changed.revision != policy_changed.revision
    with pytest.raises(ScanError, match="STALE_SNAPSHOT"):
        verify_snapshot(root, initial)


def test_symlink_directory_component_is_rejected(tmp_path):
    root = owned_fixture(tmp_path / "owned", "def safe(): pass\n")
    actual = tmp_path / "actual"
    actual.mkdir()
    (actual / "source.py").write_text("def safe(): pass\n")
    (root / "linked").symlink_to(actual, target_is_directory=True)
    (root / "manifest.json").write_text('["linked/source.py", "policy.json"]')
    with pytest.raises(ScanError):
        load_snapshot(root)
