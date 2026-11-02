#!/usr/bin/env python3
"""Run trusted project checks and validate the shipped fixed synthetic bundle offline."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def check_bundle() -> dict[str, int]:
    from lazarus_sentinel.bundle import (
        MAX_BYTES,
        parse_json,
        read_bounded,
        validate_bundle,
    )

    root = ROOT / "frontend/public/demo/v1"
    raw_manifest = read_bounded(root / "bundle.json")
    manifest = parse_json(raw_manifest)
    payloads = {
        name: read_bounded(root / name)
        for name in ("graph.json", "explanations.json")
        if (root / name).is_file()
    }
    if len(raw_manifest) + sum(map(len, payloads.values())) > MAX_BYTES:
        raise ValueError("BUNDLE_SIZE_LIMIT")
    graph = validate_bundle(manifest, payloads)
    return {
        "endpoints": sum(n.type == "API_ENDPOINT" for n in graph.nodes),
        "nodes": len(graph.nodes),
        "edges": len(graph.edges),
        "findings": len(graph.findings),
    }


def main() -> int:
    npm = shutil.which("npm")
    commands = [
        (
            "backend-tests",
            [sys.executable, "-m", "pytest", "backend/tests", "-q"],
            ROOT,
        ),
        (
            "python-lint",
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "backend/src",
                "backend/tests",
                "scripts",
            ],
            ROOT,
        ),
        (
            "python-format",
            [
                sys.executable,
                "-m",
                "ruff",
                "format",
                "--check",
                "backend/src",
                "backend/tests",
                "scripts",
            ],
            ROOT,
        ),
        (
            "python-types",
            [
                sys.executable,
                "-m",
                "mypy",
                "--config-file",
                "backend/pyproject.toml",
                "backend/src",
            ],
            ROOT,
        ),
    ]
    if npm:
        commands.extend(
            (f"frontend-{name}", [npm, "run", name], ROOT / "frontend")
            for name in ("typecheck", "lint", "test", "build")
        )
    results: list[dict[str, Any]] = []
    # Trusted application checks may execute application tests; analyzed fixtures are never imported.
    environment = {
        key: value
        for key, value in os.environ.items()
        if key.upper() in {"PATH", "HOME", "TMPDIR", "TMP", "TEMP", "SYSTEMROOT"}
    }
    environment.update(CI="true", NO_COLOR="1")
    for name, command, cwd in commands:
        start = time.monotonic()
        try:
            with tempfile.TemporaryFile() as output:
                result = subprocess.run(
                    "npm run " + name.removeprefix("frontend-")
                    if os.name == "nt" and name.startswith("frontend-")
                    else command,
                    shell=os.name == "nt" and name.startswith("frontend-"),
                    cwd=cwd,
                    env=environment,
                    stdout=output,
                    stderr=output,
                    timeout=180,
                    check=False,
                )
                output.seek(0, 2)
                output.seek(max(0, output.tell() - 4000))
                failure_tail = (
                    output.read(4000).decode("utf-8", errors="replace")
                    if result.returncode
                    else ""
                )
            code = result.returncode
        except (OSError, subprocess.TimeoutExpired):
            code = -1
            failure_tail = "CHECK_START_OR_TIMEOUT_FAILURE"
        results.append(
            {
                "check": name,
                "passed": code == 0,
                "exit_code": code,
                "elapsed_seconds": round(time.monotonic() - start, 3),
                **({"failure_output_tail": failure_tail} if code else {}),
            }
        )
    if not npm:
        results.append(
            {
                "check": "frontend-toolchain",
                "passed": False,
                "diagnostic_code": "NPM_UNAVAILABLE",
            }
        )
    counts = {}
    try:
        counts = check_bundle()
        results.append({"check": "shipped-bundle", "passed": True})
    except Exception:  # noqa: BLE001 - verification boundary emits only safe codes, never artifact contents.
        results.append(
            {
                "check": "shipped-bundle",
                "passed": False,
                "diagnostic_code": "BUNDLE_INVALID_OR_UNAVAILABLE",
            }
        )
    passed = all(result["passed"] for result in results)
    print(
        json.dumps(
            {
                "status": "PASSED" if passed else "FAILED",
                "checks": results,
                "bundle_counts": counts,
                "live_provider_attempts": 0,
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
