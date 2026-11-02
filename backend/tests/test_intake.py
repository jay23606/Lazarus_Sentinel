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


@pytest.mark.parametrize(
    "name",
    ["C:/x.py", "x:ads.py", "NUL.py", "COM1.py", "COM¹.py", "bad./x.py", "bad /x.py", "x?.py"],
)
def test_windows_reserved_paths_rejected_on_every_host(name):
    from lazarus_sentinel.intake import _path

    with pytest.raises(ScanError, match="INVALID_PATH"):
        _path(name)


def test_reparse_attribute_rejected_for_output_ancestor(tmp_path, monkeypatch):
    import stat
    from types import SimpleNamespace

    from lazarus_sentinel.intake import reject_symlink_components

    directory = tmp_path / "junction"
    directory.mkdir()
    original = Path.lstat

    def metadata(path, *args, **kwargs):
        if path == directory:
            return SimpleNamespace(
                st_mode=stat.S_IFDIR, st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT
            )
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "lstat", metadata)
    with pytest.raises(ScanError, match="SYMLINK_PATH"):
        reject_symlink_components(directory / "new-output")


def test_windows_reader_exact_case_size_and_regular_file(tmp_path):
    from lazarus_sentinel.intake import _read_windows

    fixture(tmp_path)
    assert _read_windows(tmp_path, "app.py", 100) == b"def f(): return 1\n"
    with pytest.raises(ScanError, match="PATH_ALIAS"):
        _read_windows(tmp_path, "APP.py", 100)
    with pytest.raises(ScanError, match="INVALID_FILE"):
        _read_windows(tmp_path, "app.py", 1)
    (tmp_path / "directory.py").mkdir()
    with pytest.raises(ScanError, match="INVALID_FILE"):
        _read_windows(tmp_path, "directory.py", 100)


def test_oversize_regular_file_rejected_without_symlink_privilege(tmp_path):
    fixture(tmp_path)
    (tmp_path / "app.py").write_bytes(b"x" * (256 * 1024 + 1))
    with pytest.raises(ScanError, match="INVALID_FILE"):
        load_snapshot(tmp_path)


def test_windows_real_junction_rejected_for_intake_and_output(tmp_path):
    import os
    import subprocess

    from lazarus_sentinel.intake import reject_symlink_components

    if os.name != "nt":
        pytest.skip("Native Windows junction check")
    root = tmp_path / "real"
    root.mkdir()
    fixture(root)
    alias = tmp_path / "junction"
    # Fixed trusted command; generated paths are passed as separate quoted arguments.
    result = subprocess.run(
        ["cmd.exe", "/d", "/c", "mklink", "/J", str(alias), str(root)],
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, "Windows junction creation failed"
    try:
        with pytest.raises(ScanError, match="SYMLINK_PATH"):
            load_snapshot(alias)
        with pytest.raises(ScanError, match="SYMLINK_PATH"):
            reject_symlink_components(alias / "new-output")
    finally:
        alias.rmdir()


def test_windows_reader_rechecks_file_after_close(tmp_path, monkeypatch):
    from contextlib import contextmanager

    from lazarus_sentinel.intake import _read_windows

    fixture(tmp_path)
    original = Path.open

    @contextmanager
    def changed(path, *args, **kwargs):
        with original(path, *args, **kwargs) as stream:
            yield stream
        with original(path, "ab") as stream:
            stream.write(b"changed")

    monkeypatch.setattr(Path, "open", changed)
    with pytest.raises(ScanError, match="FILE_CHANGED"):
        _read_windows(tmp_path, "app.py", 100)


def test_windows_reader_directory_enumeration_limit(tmp_path):
    from lazarus_sentinel.intake import _read_windows

    fixture(tmp_path)
    for number in range(201):
        (tmp_path / f"other-{number}").touch()
    with pytest.raises(ScanError, match="DIRECTORY_ENTRY_LIMIT"):
        _read_windows(tmp_path, "app.py", 100)
