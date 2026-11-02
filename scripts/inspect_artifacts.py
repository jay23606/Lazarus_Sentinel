#!/usr/bin/env python3
"""Bounded, read-only ledger inspection. Never repairs, deletes, or retries scans."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import stat
from pathlib import Path, PurePosixPath
from typing import Any

MAX_FILE = 16 * 1024 * 1024
MAX_ROWS = 10000
SCAN_NAME = re.compile(
    r"\.?[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?:\.staging)?"
)


def safe_path(path: Path) -> None:
    absolute = Path(os.path.abspath(path))
    for component in reversed([absolute, *absolute.parents]):
        if component.is_symlink():
            raise ValueError("SYMLINK_PATH")


def inspect(root: Path) -> dict[str, Any]:
    """Inspect only metadata and artifact bytes, never target source or source modules."""
    issues: list[dict[str, str]] = []
    safe_path(root)
    db = root / "sentinel.sqlite3"
    safe_path(db)
    if not db.is_file() or db.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("DATABASE_MISSING_OR_OVERSIZE")
    with sqlite3.connect(
        db.absolute().as_uri() + "?mode=ro", uri=True, timeout=2
    ) as connection:
        connection.execute("PRAGMA query_only=ON")
        if connection.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
            raise ValueError("DATABASE_INTEGRITY_FAILED")
        scans = connection.execute(
            "SELECT scan_id,status FROM scans LIMIT ?", (MAX_ROWS + 1,)
        ).fetchall()
        refs = connection.execute(
            "SELECT scan_id,kind,path,sha256,size FROM artifact_refs LIMIT ?",
            (MAX_ROWS + 1,),
        ).fetchall()
    if len(scans) > MAX_ROWS or len(refs) > MAX_ROWS:
        raise ValueError("LEDGER_ROW_LIMIT")
    statuses = dict(scans)
    committed_dirs = set()
    checked = 0
    expected_kinds = {"graph.json", "findings.json", "coverage.json", "report.md"}
    for scan_id, status in scans:
        if (
            status in {"COMPLETED", "PARTIAL"}
            and {r[1] for r in refs if r[0] == scan_id} != expected_kinds
        ):
            issues.append(
                {
                    "scan_id": scan_id
                    if SCAN_NAME.fullmatch(scan_id)
                    else "invalid-id",
                    "code": "ARTIFACT_REF_SET_INVALID",
                }
            )
    for scan_id, kind, relative, digest, size in refs:
        label = (
            scan_id
            if isinstance(scan_id, str) and SCAN_NAME.fullmatch(scan_id)
            else "invalid-id"
        )
        try:
            if (
                kind not in expected_kinds
                or not isinstance(relative, str)
                or "\\" in relative
            ):
                raise ValueError("INVALID_ARTIFACT_PATH")
            parts = PurePosixPath(relative)
            if (
                parts.is_absolute()
                or ".." in parts.parts
                or len(parts.parts) != 3
                or parts.parts[:2] != ("scans", scan_id)
                or parts.name != kind
            ):
                raise ValueError("INVALID_ARTIFACT_PATH")
            if statuses.get(scan_id) not in {"COMPLETED", "PARTIAL"}:
                raise ValueError("REF_FOR_UNCOMMITTED_SCAN")
            if not isinstance(size, int) or size < 0 or size > MAX_FILE:
                raise ValueError("ARTIFACT_SIZE_LIMIT")
            path = root.joinpath(*parts.parts)
            safe_path(path)
            metadata = path.lstat()
            if not stat.S_ISREG(metadata.st_mode):
                raise ValueError("ARTIFACT_SIZE_OR_TYPE")
            descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(descriptor, "rb") as file:
                metadata = os.fstat(file.fileno())
                if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_FILE:
                    raise ValueError("ARTIFACT_SIZE_OR_TYPE")
                data = file.read(MAX_FILE + 1)
            if len(data) != size or hashlib.sha256(data).hexdigest() != digest:
                raise ValueError("ARTIFACT_HASH_OR_SIZE_MISMATCH")
            if kind.endswith(".json"):
                json.loads(data)
            committed_dirs.add(scan_id)
            checked += 1
        except (OSError, ValueError, TypeError, RecursionError):
            issues.append({"scan_id": label, "code": "ARTIFACT_INVALID"})
    scans_root = root / "scans"
    safe_path(scans_root)
    if scans_root.exists():
        with os.scandir(scans_root) as directories:
            for count, entry in enumerate(directories, 1):
                if count > MAX_ROWS:
                    raise ValueError("SCAN_DIRECTORY_LIMIT")
                name = entry.name if SCAN_NAME.fullmatch(entry.name) else "invalid-name"
                if entry.is_symlink() or not entry.is_dir(follow_symlinks=False):
                    issues.append({"scan_id": name, "code": "UNEXPECTED_SCAN_ENTRY"})
                elif entry.name not in committed_dirs:
                    issues.append(
                        {"scan_id": name, "code": "ORPHAN_OR_UNCOMMITTED_DIRECTORY"}
                    )
    for scan_id, status in scans:
        if status == "RUNNING":
            issues.append(
                {
                    "scan_id": scan_id
                    if SCAN_NAME.fullmatch(scan_id)
                    else "invalid-id",
                    "code": "INTERRUPTED_OR_ACTIVE_SCAN_NO_RETRY",
                }
            )
    return {
        "status": "ISSUES" if issues else "OK",
        "scans": len(scans),
        "artifact_refs": len(refs),
        "verified_artifacts": checked,
        "issues": issues,
        "mutations": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1] / "artifacts"
    )
    args = parser.parse_args(argv)
    try:
        result = inspect(args.root)
    except (OSError, ValueError, sqlite3.Error):
        result = {
            "status": "ERROR",
            "diagnostic_codes": ["INSPECTION_FAILED"],
            "mutations": False,
        }
    print(json.dumps(result, sort_keys=True))
    return {"OK": 0, "ISSUES": 2, "ERROR": 1}[str(result["status"])]


if __name__ == "__main__":
    raise SystemExit(main())
