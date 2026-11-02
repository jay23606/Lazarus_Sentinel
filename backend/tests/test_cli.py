import json

from lazarus_sentinel.cli import main


def test_invalid_target(capsys):
    assert main(["scan", "--target", "/etc/passwd"]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["diagnostic_codes"] == ["INVALID_TARGET"]


def test_unexpected_error_is_sanitized(capsys, monkeypatch):
    def broken(*args):
        raise KeyError("credential /private/secret")

    monkeypatch.setattr("lazarus_sentinel.cli.scan", broken)
    assert main(["scan", "--target", "fixture:fastapi-demo"]) == 1
    output = capsys.readouterr()
    assert "credential" not in output.out + output.err
    assert json.loads(output.out)["diagnostic_codes"] == ["INTERNAL_ERROR"]
