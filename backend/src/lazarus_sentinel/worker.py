"""Credential-free parser subprocess with bounded input, output and wall clock."""

from __future__ import annotations

import math
import os
import subprocess
import sys
import tempfile
import time

from .intake import ScanError
from .models import Graph, Snapshot

MAX_INPUT = 8 * 1024 * 1024
MAX_OUTPUT = 16 * 1024 * 1024


def _environment() -> dict[str, str]:
    return {"PATH": os.defpath, "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"}


def analyze_snapshot(snapshot: Snapshot, timeout_seconds: float = 30) -> Graph:
    if not math.isfinite(timeout_seconds) or timeout_seconds <= 0 or timeout_seconds > 30:
        raise ScanError("INVALID_TIMEOUT")
    payload = snapshot.model_dump_json().encode()
    if len(payload) > MAX_INPUT:
        raise ScanError("WORKER_INPUT_LIMIT")
    with tempfile.TemporaryFile() as input_file, tempfile.TemporaryFile() as output_file:
        input_file.write(payload)
        input_file.seek(0)
        try:
            process = subprocess.Popen(
                [sys.executable, "-I", "-m", "lazarus_sentinel.worker"],
                stdin=input_file,
                stdout=output_file,
                stderr=subprocess.DEVNULL,
                env=_environment(),
                cwd=tempfile.gettempdir(),
                start_new_session=True,
            )
        except OSError:
            raise ScanError("WORKER_START_FAILED") from None
        deadline = time.monotonic() + timeout_seconds
        try:
            while process.poll() is None:
                if time.monotonic() >= deadline:
                    raise ScanError("WORKER_TIMEOUT")
                if os.fstat(output_file.fileno()).st_size > MAX_OUTPUT:
                    raise ScanError("WORKER_OUTPUT_LIMIT")
                time.sleep(0.01)
            if process.returncode:
                raise ScanError("WORKER_FAILED")
            output_file.seek(0)
            result = output_file.read(MAX_OUTPUT + 1)
            if len(result) > MAX_OUTPUT:
                raise ScanError("WORKER_OUTPUT_LIMIT")
            try:
                return Graph.model_validate_json(result)
            except ValueError:
                raise ScanError("WORKER_INVALID_OUTPUT") from None
        finally:
            if process.poll() is None:
                process.kill()
            process.wait()


def _main() -> None:
    # Limit parser accidents; this is a process boundary, not an OS network sandbox.
    import resource

    resource.setrlimit(resource.RLIMIT_CPU, (25, 25))
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT, MAX_OUTPUT))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    from .analysis import analyze

    data = sys.stdin.buffer.read(MAX_INPUT + 1)
    if len(data) > MAX_INPUT:
        raise SystemExit(2)
    try:
        snapshot = Snapshot.model_validate_json(data)
        graph = analyze(snapshot)
        result = graph.model_dump_json().encode()
        if len(result) > MAX_OUTPUT:
            raise SystemExit(2)
        sys.stdout.buffer.write(result)
    except Exception:  # noqa: BLE001 - child boundary must never emit raw parser errors.
        raise SystemExit(2) from None


if __name__ == "__main__":
    _main()
