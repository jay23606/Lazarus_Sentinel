import json

from lazarus_sentinel.cli import main


def test_explain_defaults_disabled(capsys, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "lazarus_sentinel.cli.explain_finding",
        lambda *args: calls.append(args) or {"status": "DISABLED", "provider": "disabled"},
    )
    assert main(["explain", "--scan-id", "scan", "--finding-id", "finding"]) == 0
    assert calls == [("scan", "finding", "disabled")]
    assert json.loads(capsys.readouterr().out)["status"] == "DISABLED"


def test_export_dispatch(capsys, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "lazarus_sentinel.cli.export_demo_bundle",
        lambda *args: calls.append(args) or {"status": "EXPORTED"},
    )
    assert main(["demo", "export", "--scan-id", "scan", "--annotation-id", "annotation"]) == 0
    assert calls == [("scan", "annotation")]
    assert json.loads(capsys.readouterr().out)["status"] == "EXPORTED"


def test_demo_failure_sanitized(capsys, monkeypatch):
    def broken(*args):
        raise ValueError("credential /private/secret")

    monkeypatch.setattr("lazarus_sentinel.cli.export_demo_bundle", broken)
    assert main(["demo", "export", "--scan-id", "scan"]) == 1
    output = capsys.readouterr()
    assert "credential" not in output.out + output.err
    assert json.loads(output.out)["diagnostic_codes"] == ["INTERNAL_ERROR"]


def test_real_disabled_and_mock_cli_preserve_scan_and_budget(tmp_path, monkeypatch, capsys):
    import shutil

    from lazarus_sentinel import bundle, explanations, meta_provider, service

    shutil.copytree(service.FIXTURE_ROOT, tmp_path / "fixtures" / "fastapi_demo")
    for module in (bundle, explanations, service):
        monkeypatch.setattr(module, "WORKSPACE", tmp_path)

    def no_transport(*args, **kwargs):
        raise AssertionError("NO_EGRESS_ALLOWED")

    monkeypatch.setattr(meta_provider, "generate", no_transport)
    scan = service.scan("fixture:fastapi-demo", tmp_path / "artifacts")
    loaded = bundle.load_committed_graph(scan["scan_id"])
    original = {
        p: p.read_bytes() for p in (tmp_path / "artifacts" / "scans").rglob("*") if p.is_file()
    }
    finding = loaded.graph.findings[0]
    args = ["explain", "--scan-id", scan["scan_id"], "--finding-id", finding.id]
    assert main(args) == 0
    assert json.loads(capsys.readouterr().out) == {"status": "DISABLED", "provider": "disabled"}
    assert not (tmp_path / "artifacts" / "explanations").exists()
    assert main([*args, "--provider", "mock"]) == 0
    annotation = json.loads(capsys.readouterr().out)
    assert (
        main(
            [
                "demo",
                "export",
                "--scan-id",
                scan["scan_id"],
                "--annotation-id",
                annotation["annotation_id"],
            ]
        )
        == 0
    )
    exported = json.loads(capsys.readouterr().out)
    directory = tmp_path / exported["artifact_dir"]
    manifest = json.loads((directory / "bundle.json").read_bytes())
    payloads = {name: (directory / name).read_bytes() for name in manifest["artifacts"]}
    assert bundle.validate_bundle(manifest, payloads) == loaded.graph
    assert payloads["graph.json"] == loaded.graph_bytes
    assert all(path.read_bytes() == data for path, data in original.items())
    assert not (tmp_path / "artifacts" / "model-budget.sqlite3").exists()


def test_known_gate_codes_survive_cli_without_raw_errors(capsys, monkeypatch):
    for code in (
        "META_KEY_MISSING",
        "META_DEADLINE_EXCEEDED",
        "BUDGET_RECONCILIATION_REQUIRED",
        "ARTIFACT_HASH_MISMATCH",
    ):

        def blocked(*args, code=code):
            raise ValueError(code)

        monkeypatch.setattr("lazarus_sentinel.cli.explain_finding", blocked)
        assert (
            main(["explain", "--scan-id", "scan", "--finding-id", "finding", "--provider", "meta"])
            == 1
        )
        assert json.loads(capsys.readouterr().out)["diagnostic_codes"] == [code]
