from lazarus_sentinel.persistence import Store


def test_recovery_and_reload(tmp_path):
    store = Store(tmp_path)
    with store.writer():
        store.start("one")
    store.close()
    store = Store(tmp_path)
    with store.writer():
        assert store.get("one")["status"] == "FAILED"
        assert store.get("one")["artifacts"] == []
        store.start("two")
        store.finish(
            {"scan_id": "two", "status": "COMPLETED"},
            refs=[("graph", "scans/two/graph.json", "hash", 1)],
        )
    store.close()
    store = Store(tmp_path)
    assert store.get("two")["artifacts"][0]["kind"] == "graph"
    store.close()


def test_failed_commit_exposes_no_refs(tmp_path):
    import sqlite3

    import pytest

    store = Store(tmp_path)
    with store.writer():
        store.start("one")
        with pytest.raises(sqlite3.IntegrityError):
            store.finish(
                {"scan_id": "one", "status": "COMPLETED"},
                refs=[("graph", "first", "h", 1), ("graph", "second", "h", 1)],
            )
        assert store.get("one")["status"] == "RUNNING"
        assert store.get("one")["artifacts"] == []
    store.close()


def test_second_writer_cannot_recover_active_scan(tmp_path):
    import sqlite3
    import threading

    entered = threading.Event()
    errors = []

    def second_writer():
        other = Store(tmp_path)
        try:
            with other.writer():
                entered.set()
        except (OSError, sqlite3.Error) as error:
            errors.append(error)
        finally:
            other.close()

    store = Store(tmp_path)
    with store.writer():
        store.start("active")
        thread = threading.Thread(target=second_writer)
        thread.start()
        assert not entered.wait(0.05)
        assert store.get("active")["status"] == "RUNNING"
        store.finish({"scan_id": "active", "status": "COMPLETED"})
    thread.join(2)
    assert entered.is_set()
    assert not errors
    assert store.get("active")["status"] == "COMPLETED"
    store.close()


def _hold_writer(root, entered, release):
    store = Store(root)
    try:
        with store.writer():
            entered.set()
            if release is None:
                import time

                time.sleep(20)
            else:
                release.wait(20)
    finally:
        store.close()


def test_spawn_writer_exclusion_and_crash_release(tmp_path):
    import multiprocessing

    context = multiprocessing.get_context("spawn")
    first_entered, second_entered = context.Event(), context.Event()
    release = context.Event()
    Store(tmp_path).close()
    first = context.Process(target=_hold_writer, args=(tmp_path, first_entered, None))
    second = context.Process(target=_hold_writer, args=(tmp_path, second_entered, release))
    first.start()
    try:
        assert first_entered.wait(5)
        second.start()
        assert not second_entered.wait(0.2)
        first.terminate()
        first.join(5)
        assert not first.is_alive()
        assert second_entered.wait(5), "OS must release the terminated writer's lock"
        release.set()
        second.join(5)
        assert second.exitcode == 0
    finally:
        release.set()
        for child in (first, second):
            if child.pid is not None:
                if child.is_alive():
                    child.kill()
                child.join(5)
                child.close()


def test_windows_fixed_byte_lock_and_bounded_contention(tmp_path, monkeypatch):
    from types import SimpleNamespace

    import pytest

    from lazarus_sentinel import persistence

    store = Store(tmp_path)
    calls = []

    def locking(descriptor, mode, count):
        import os

        calls.append((mode, count, os.lseek(descriptor, 0, os.SEEK_CUR)))

    with monkeypatch.context() as patch:
        patch.setattr(persistence.sys, "platform", "win32")
        patch.setattr(
            persistence,
            "msvcrt",
            SimpleNamespace(locking=locking, LK_NBLCK=1, LK_UNLCK=2),
            raising=False,
        )
        with store.writer():
            assert calls == [(1, 1, 0)]
        assert calls == [(1, 1, 0), (2, 1, 0)]
        assert (tmp_path / ".scan.lock").read_bytes() == b"\0"

        def blocked(*args):
            raise PermissionError("busy")

        patch.setattr(persistence.msvcrt, "locking", blocked)
        ticks = iter([0, 31])
        patch.setattr(persistence.time, "monotonic", lambda: next(ticks))
        with pytest.raises(TimeoutError, match="SCAN_LOCK_TIMEOUT"), store.writer():
            pytest.fail("must not enter after lock timeout")
    store.close()
