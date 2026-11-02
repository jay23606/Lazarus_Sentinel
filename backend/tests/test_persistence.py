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
