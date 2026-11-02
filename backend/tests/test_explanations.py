import pytest

from lazarus_sentinel.explanations import explain_finding


def test_disabled_has_no_effects():
    assert explain_finding("invalid", "invalid") == {"status": "DISABLED", "provider": "disabled"}


def test_unknown_provider_rejected():
    with pytest.raises(ValueError):
        explain_finding("invalid", "invalid", "other")


import json

from test_bundle import committed_scan as _committed_scan

from lazarus_sentinel.bundle import export_demo_bundle, load_committed_graph
from lazarus_sentinel.explanations import build_request, validate_annotation


@pytest.fixture
def committed_scan(tmp_path, monkeypatch):
    return _committed_scan.__wrapped__(tmp_path, monkeypatch)


def test_mock_sidecar_binding_and_immutable_scans(committed_scan):
    root, scan_id = committed_scan
    loaded = load_committed_graph(scan_id)
    finding = loaded.graph.findings[0]
    first = explain_finding(scan_id, finding.id, "mock")
    second = explain_finding(scan_id, finding.id, "mock")
    assert first["annotation_id"] != second["annotation_id"]
    annotation = json.loads((root / first["artifact_path"]).read_bytes())
    assert validate_annotation(annotation, loaded).generation == "mock"
    assert load_committed_graph(scan_id).graph_bytes == loaded.graph_bytes
    exported = export_demo_bundle(scan_id, first["annotation_id"])
    assert (root / exported["artifact_dir"] / "explanations.json").is_file()
    assert len(build_request(loaded, finding.id, "mock")["context"]["evidence"]) > 0
    annotation["response"]["evidence_ids"] = ["invented"]
    with pytest.raises(ValueError, match="INVALID_CITATIONS"):
        validate_annotation(annotation, loaded)


@pytest.mark.parametrize(
    "field,value",
    [("request_sha256", "0" * 64), ("graph_sha256", "0" * 64), ("finding_id", "missing")],
)
def test_annotation_rebinding_rejected(committed_scan, field, value):
    root, scan_id = committed_scan
    loaded = load_committed_graph(scan_id)
    result = explain_finding(scan_id, loaded.graph.findings[0].id, "mock")
    annotation = json.loads((root / result["artifact_path"]).read_bytes())
    annotation[field] = value
    with pytest.raises(ValueError):
        validate_annotation(annotation, loaded)


def test_context_and_response_boundaries(committed_scan):
    from lazarus_sentinel.demo_models import ExplanationResponse

    _root, scan_id = committed_scan
    loaded = load_committed_graph(scan_id)
    finding = loaded.graph.findings[0]
    finding.assumptions = ["x" * 20000]
    with pytest.raises(ValueError, match="CONTEXT_SIZE_LIMIT"):
        build_request(loaded, finding.id, "mock")
    base = {"summary": "s", "why_it_matters": "w", "limitations": ["l"], "evidence_ids": ["e"]}
    for change in (
        {"summary": " "},
        {"summary": "x" * 2001},
        {"evidence_ids": ["e", "e"]},
        {"severity": "HIGH"},
    ):
        with pytest.raises(ValueError):
            ExplanationResponse.model_validate(base | change)
