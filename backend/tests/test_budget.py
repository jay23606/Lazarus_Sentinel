from lazarus_sentinel.budget import Budget


def test_budget_ambiguous_attempt_blocks(tmp_path):
    budget = Budget(tmp_path / "budget.sqlite3")
    budget.reserve(1000)
    try:
        budget.reserve(1000)
    except ValueError as error:
        assert str(error) == "BUDGET_RECONCILIATION_REQUIRED"
    else:
        raise AssertionError("ambiguous attempts must block")


import multiprocessing
import sqlite3

import pytest


def _reserve(path, ready):
    try:
        Budget(path).reserve(1024)
        ready.put("reserved")
    except ValueError:
        ready.put("blocked")


def test_concurrent_reservations_one_transport_only(tmp_path):
    context = multiprocessing.get_context("fork")
    ready = context.Queue()
    path = tmp_path / "budget.sqlite3"
    Budget(path)
    workers = [context.Process(target=_reserve, args=(path, ready)) for _ in range(4)]
    for process in workers:
        process.start()
    for process in workers:
        process.join(5)
        assert process.exitcode == 0
    assert sorted(ready.get(timeout=1) for _ in workers) == ["blocked"] * 3 + ["reserved"]


def test_attempt_cap_and_monotonic_ledger(tmp_path):
    budget = Budget(tmp_path / "budget.sqlite3")
    for _ in range(5):
        identity = budget.reserve(1024)
        budget.settle(identity, 100, 20)
    with pytest.raises(ValueError, match="BUDGET_EXHAUSTED"):
        budget.reserve(1024)
    with sqlite3.connect(budget.path) as db:
        assert db.execute("SELECT COUNT(*) FROM attempts").fetchone()[0] == 5


def test_invalid_usage_keeps_reservation(tmp_path):
    budget = Budget(tmp_path / "budget.sqlite3")
    identity = budget.reserve(1024)
    with pytest.raises(ValueError):
        budget.settle(identity, 1000000, 1)
    with pytest.raises(ValueError, match="RECONCILIATION"):
        budget.reserve(1024)
