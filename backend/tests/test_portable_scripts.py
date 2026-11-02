"""Exercise the standalone read-only inspector against application-owned artifacts."""

import importlib.util
from pathlib import Path

import pytest

from lazarus_sentinel.service import scan


def inspector():
    path = Path(__file__).resolve().parents[2] / "scripts" / "inspect_artifacts.py"
    spec = importlib.util.spec_from_file_location("inspect_artifacts", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_inspector_verifies_artifacts_and_detects_changes(tmp_path):
    result = scan("fixture:fastapi-demo", tmp_path)
    tool = inspector()
    assert tool.inspect(tmp_path)["verified_artifacts"] == 4
    report = tmp_path / result["artifact_dir"] / "report.md"
    report.write_bytes(b"changed")
    assert tool.inspect(tmp_path)["status"] == "ISSUES"


def test_inspector_rejects_reparse_attribute(tmp_path, monkeypatch):
    import stat
    from types import SimpleNamespace

    original = Path.lstat

    def metadata(path, *args, **kwargs):
        if path == tmp_path:
            return SimpleNamespace(
                st_mode=stat.S_IFDIR, st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT
            )
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "lstat", metadata)
    with pytest.raises(ValueError, match="SYMLINK_PATH"):
        inspector().safe_path(tmp_path)


@pytest.mark.parametrize("scan_id", ["C:", "NUL", "COM1", "123.staging"])
def test_inspector_rejects_non_uuid_ref_before_path_join(tmp_path, monkeypatch, scan_id):
    import sqlite3

    from lazarus_sentinel.persistence import Store

    store = Store(tmp_path)
    store.close()
    with sqlite3.connect(tmp_path / "sentinel.sqlite3") as db:
        db.execute("INSERT INTO scans VALUES(?,?,?)", (scan_id, "PARTIAL", "{}"))
        db.execute(
            "INSERT INTO artifact_refs VALUES(?,?,?,?,?)",
            (scan_id, "graph.json", f"scans/{scan_id}/graph.json", "a" * 64, 1),
        )
    original = Path.joinpath

    def guarded(path, *parts):
        assert scan_id not in parts, "invalid scan id reached artifact path join"
        return original(path, *parts)

    monkeypatch.setattr(Path, "joinpath", guarded)
    assert inspector().inspect(tmp_path)["status"] == "ISSUES"
