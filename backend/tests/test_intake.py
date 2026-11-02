import json
from pathlib import Path

import pytest

from lazarus_sentinel.intake import ScanError, load_snapshot, verify_snapshot
from lazarus_sentinel.models import source_bytes


def fixture(root: Path) -> Path:
    (root / "app.py").write_bytes(b"def f(): return 1\n")
    (root / "policy.json").write_text('{"protected_operations": []}')
    (root / "manifest.json").write_text(json.dumps(["app.py", "policy.json"]))
    return root


def test_snapshot_revision_stale_and_exact_bytes(tmp_path):
    root = fixture(tmp_path)
    snapshot = load_snapshot(root)
    assert source_bytes(snapshot, "app.py") == (root / "app.py").read_bytes()
    assert load_snapshot(root).revision == snapshot.revision
    verify_snapshot(root, snapshot)
    (root / "app.py").write_text("changed")
    with pytest.raises(ScanError, match="STALE_SNAPSHOT"):
        verify_snapshot(root, snapshot)


@pytest.mark.parametrize("path", ["../app.py", "/tmp/app.py", "./app.py", "x/../app.py"])
def test_reject_paths(tmp_path, path):
    fixture(tmp_path)
    (tmp_path / "manifest.json").write_text(json.dumps([path, "policy.json"]))
    with pytest.raises(ScanError):
        load_snapshot(tmp_path)


def test_reject_symlinks_and_oversize(tmp_path):
    fixture(tmp_path)
    (tmp_path / "app.py").unlink()
    (tmp_path / "app.py").symlink_to("policy.json")
    with pytest.raises(ScanError):
        load_snapshot(tmp_path)
    (tmp_path / "app.py").unlink()
    (tmp_path / "app.py").write_bytes(b"x" * (256 * 1024 + 1))
    with pytest.raises(ScanError):
        load_snapshot(tmp_path)


def test_policy_change_changes_revision(tmp_path):
    fixture(tmp_path)
    first = load_snapshot(tmp_path)
    (tmp_path / "policy.json").write_text('{ "protected_operations": [] }')
    assert load_snapshot(tmp_path).revision != first.revision


def test_reject_directory_enumeration_limit(tmp_path):
    fixture(tmp_path)
    for number in range(201):
        (tmp_path / f"other-{number}").touch()
    with pytest.raises(ScanError, match="DIRECTORY_ENTRY_LIMIT"):
        load_snapshot(tmp_path)


def test_total_budget_is_applied_before_read(tmp_path, monkeypatch):
    fixture(tmp_path)
    monkeypatch.setattr("lazarus_sentinel.intake.MAX_TOTAL_BYTES", 2)
    with pytest.raises(ScanError, match="INVALID_FILE"):
        load_snapshot(tmp_path)


def test_reject_fixture_root_symlink_ancestor(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    target = real / "fixture"
    target.mkdir()
    fixture(target)
    alias = tmp_path / "alias"
    alias.symlink_to(real, target_is_directory=True)
    with pytest.raises(ScanError):
        load_snapshot(alias / "fixture")


def test_output_path_precheck_rejects_ancestor_and_dangling_symlinks(tmp_path):
    from lazarus_sentinel.intake import reject_symlink_components

    target = tmp_path / "real"
    target.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(target, target_is_directory=True)
    with pytest.raises(ScanError, match="SYMLINK_PATH"):
        reject_symlink_components(alias / "not-created" / "output")
    dangling = tmp_path / "dangling"
    dangling.symlink_to(tmp_path / "missing")
    with pytest.raises(ScanError, match="SYMLINK_PATH"):
        reject_symlink_components(dangling)
    reject_symlink_components(target / "new" / "output")
    with pytest.raises(ScanError, match="INVALID_PATH"):
        reject_symlink_components(target / ".." / "output")
