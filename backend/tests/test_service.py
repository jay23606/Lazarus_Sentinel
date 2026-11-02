import pytest

from lazarus_sentinel.service import scan


def test_scan_serializes_windows_relative_paths_as_posix(tmp_path, monkeypatch):
    from pathlib import Path, PureWindowsPath

    from lazarus_sentinel.persistence import Store

    original = Path.relative_to

    def windows_relative(path, *args, **kwargs):
        return PureWindowsPath(*original(path, *args, **kwargs).parts)

    monkeypatch.setattr(Path, "relative_to", windows_relative)
    result = scan("fixture:fastapi-demo", tmp_path)
    assert result["status"] == "PARTIAL"
    assert result["artifact_dir"] == f"scans/{result['scan_id']}"
    store = Store(tmp_path)
    try:
        references = store.get(result["scan_id"])["artifacts"]
        assert len(references) == 4
        assert all(
            reference["path"] == f"scans/{result['scan_id']}/{reference['kind']}"
            for reference in references
        )
    finally:
        store.close()


def test_invalid_target_never_reads(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.read_bytes", lambda *args: pytest.fail("read attempted"))
    result = scan("/etc/passwd", tmp_path)
    assert result["status"] == "FAILED"
    assert result["diagnostic_codes"] == ["INVALID_TARGET"]


def test_source_recheck_failure_commits_no_artifacts(tmp_path, monkeypatch):
    from lazarus_sentinel.intake import ScanError
    from lazarus_sentinel.persistence import Store

    monkeypatch.setattr(
        "lazarus_sentinel.service.intake.verify_snapshot",
        lambda *args: (_ for _ in ()).throw(ScanError("STALE_SNAPSHOT")),
    )
    result = scan("fixture:fastapi-demo", tmp_path)
    assert result["status"] == "FAILED"
    store = Store(tmp_path)
    assert store.get(result["scan_id"])["artifacts"] == []
    store.close()


def test_repeat_scan_stable_findings_and_hash_only_report(tmp_path):
    import json

    first = scan("fixture:fastapi-demo", tmp_path)
    second = scan("fixture:fastapi-demo", tmp_path)
    assert first["status"] == second["status"] == "PARTIAL"
    one = json.loads((tmp_path / first["artifact_dir"] / "findings.json").read_text())
    two = json.loads((tmp_path / second["artifact_dir"] / "findings.json").read_text())
    assert [f["id"] for f in one["findings"]] == [f["id"] for f in two["findings"]]
    assert len(one["findings"]) == 2
    graph = json.loads((tmp_path / first["artifact_dir"] / "graph.json").read_text())
    names = {n["id"]: n["qualified_name"] for n in graph["nodes"]}
    endpoints = {names[f["entry_node_id"]] for f in one["findings"]}
    assert endpoints == {
        "app.main.weak_export:GET /weak",
        "app.main.authenticated_export:GET /authenticated",
    }
    report = (tmp_path / first["artifact_dir"] / "report.md").read_text()
    assert "def " not in report
    assert "excerpt_redacted" not in report
    assert str(tmp_path) not in report


@pytest.mark.parametrize("alias", ["root", "scans", "sentinel.sqlite3", ".scan.lock"])
def test_artifact_symlink_rejected_without_target_writes(tmp_path, alias):
    outside = tmp_path / "outside"
    outside.mkdir()
    root = tmp_path / "artifacts"
    if alias == "root":
        root.symlink_to(outside, target_is_directory=True)
    else:
        root.mkdir()
        (root / alias).symlink_to(outside, target_is_directory=True)
    result = scan("fixture:fastapi-demo", root)
    assert result["status"] == "FAILED"
    assert list(outside.iterdir()) == []


@pytest.mark.parametrize("alias", ["sentinel.sqlite3", ".scan.lock"])
def test_output_file_alias_rejected_before_open(tmp_path, alias):
    root = tmp_path / "artifacts"
    root.mkdir()
    outside = tmp_path / "outside-file"
    outside.write_bytes(b"")
    (root / alias).symlink_to(outside)
    result = scan("fixture:fastapi-demo", root)
    assert result["status"] == "FAILED"
    assert outside.read_bytes() == b""
