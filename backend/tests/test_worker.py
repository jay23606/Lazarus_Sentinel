from unittest.mock import patch

import pytest

from lazarus_sentinel.intake import ScanError
from lazarus_sentinel.worker import _environment, analyze_snapshot


def test_worker_environment_has_no_credentials():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "never-forward", "HOME": "/private/home"}):
        assert "OPENAI_API_KEY" not in _environment()
        assert "HOME" not in _environment()


def test_worker_rejects_invalid_timeout():
    with pytest.raises(ScanError, match="INVALID_TIMEOUT"):
        analyze_snapshot(None, timeout_seconds=0)


def test_timeout_kills_original_process_without_retry():
    from unittest.mock import Mock

    from lazarus_sentinel.models import SecurityPolicy, Snapshot

    snapshot = Snapshot(
        revision="r",
        files={},
        file_hashes={},
        manifest_base64="",
        policy_base64="",
        policy_hash="",
        policy=SecurityPolicy(protected_operations=[]),
    )
    process = Mock()
    process.poll.return_value = None
    with (
        patch("lazarus_sentinel.worker.subprocess.Popen", return_value=process) as spawn,
        patch("lazarus_sentinel.worker.time.monotonic", side_effect=[0, 31]),
        pytest.raises(ScanError, match="WORKER_TIMEOUT"),
    ):
        analyze_snapshot(snapshot)
    spawn.assert_called_once()
    process.kill.assert_called_once()
    process.wait.assert_called_once()


def test_isolated_worker_analyzes_owned_fixture():
    from pathlib import Path

    from lazarus_sentinel.intake import load_snapshot

    root = Path(__file__).resolve().parents[2] / "fixtures" / "fastapi_demo"
    snapshot = load_snapshot(root)
    graph = analyze_snapshot(snapshot)
    assert graph.repository["revision"] == snapshot.revision
    assert any(node.type == "API_ENDPOINT" for node in graph.nodes)
