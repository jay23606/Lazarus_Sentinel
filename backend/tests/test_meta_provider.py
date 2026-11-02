import pytest

from lazarus_sentinel.meta_provider import generate


def test_missing_key_never_opens_ledger(monkeypatch, tmp_path):
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    with pytest.raises(ValueError, match="META_KEY_MISSING"):
        generate(b"{}", tmp_path / "budget.sqlite3")
    assert not (tmp_path / "budget.sqlite3").exists()


import json
import time

from lazarus_sentinel import meta_provider


def request_bytes():
    return json.dumps(
        {
            "model": "muse-spark-1.3",
            "messages": [],
            "max_completion_tokens": 1024,
            "response_format": {"type": "json_object"},
            "stream": False,
        }
    ).encode()


def test_usage_settled_and_response_returned(monkeypatch, tmp_path):
    monkeypatch.setenv("MODEL_API_KEY", "fake-test-key")
    monkeypatch.setattr(
        meta_provider,
        "bounded_transport",
        lambda *args: {
            "usage": {"prompt_tokens": 100, "completion_tokens": 20},
            "choices": [{"message": {"content": '{"summary":"test"}'}}],
        },
    )
    assert generate(request_bytes(), tmp_path / "budget.sqlite3") == {"summary": "test"}


def test_failed_transport_retains_reservation(monkeypatch, tmp_path):
    monkeypatch.setenv("MODEL_API_KEY", "fake-test-key")
    calls = []

    def fail(*args):
        calls.append(1)
        raise ValueError("redacted")

    monkeypatch.setattr(meta_provider, "bounded_transport", fail)
    for _ in range(2):
        with pytest.raises(ValueError):
            generate(request_bytes(), tmp_path / "budget.sqlite3")
    assert calls == [1]


def test_absolute_deadline_kills_child(monkeypatch):
    monkeypatch.setattr(meta_provider, "DEADLINE_SECONDS", 0.1)

    def hang(*args):
        time.sleep(5)

    monkeypatch.setattr(meta_provider, "_transport", hang)
    started = time.monotonic()
    with pytest.raises(ValueError, match="DEADLINE"):
        meta_provider.bounded_transport(b"{}", "fake")
    assert time.monotonic() - started < 2


def test_child_errors_are_redacted(monkeypatch):
    def fail(*args):
        raise RuntimeError("fake-test-secret")

    monkeypatch.setattr(meta_provider, "_transport", fail)
    with pytest.raises(ValueError, match="^META_TRANSPORT_FAILED$"):
        meta_provider.bounded_transport(b"{}", "fake")


def test_unexpected_tool_call_refused(monkeypatch, tmp_path):
    monkeypatch.setenv("MODEL_API_KEY", "fake-test-key")
    monkeypatch.setattr(
        meta_provider,
        "bounded_transport",
        lambda *args: {
            "usage": {"prompt_tokens": 100, "completion_tokens": 20},
            "choices": [
                {
                    "finish_reason": "tool_calls",
                    "message": {
                        "content": '{"summary":"test"}',
                        "tool_calls": [{"id": "unexpected"}],
                    },
                }
            ],
        },
    )
    with pytest.raises(ValueError, match="META_UNEXPECTED_TOOLS"):
        generate(request_bytes(), tmp_path / "budget.sqlite3")
