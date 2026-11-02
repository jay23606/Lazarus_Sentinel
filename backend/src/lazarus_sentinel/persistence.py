"""Single-writer scan ledger; readers only see committed artifact references."""

from __future__ import annotations

import contextlib
import fcntl
import json
import sqlite3
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any

from .intake import reject_symlink_components
from .models import Finding


class Store:
    def __init__(self, root: Path):
        self.root = root
        for path in (root, root / "scans", root / "sentinel.sqlite3", root / ".scan.lock"):
            reject_symlink_components(path)
        root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.db = sqlite3.connect(root / "sentinel.sqlite3")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS scans(scan_id TEXT PRIMARY KEY,status TEXT NOT NULL,summary TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS findings(scan_id TEXT,finding_id TEXT,body TEXT NOT NULL,PRIMARY KEY(scan_id,finding_id));
        CREATE TABLE IF NOT EXISTS artifact_refs(scan_id TEXT,kind TEXT,path TEXT NOT NULL,sha256 TEXT NOT NULL,size INTEGER NOT NULL,PRIMARY KEY(scan_id,kind));
        """)
        self.db.commit()

    @contextlib.contextmanager
    def writer(self) -> Iterator[None]:
        reject_symlink_components(self.root / ".scan.lock")
        with (self.root / ".scan.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                with self.db:
                    self.db.execute(
                        "UPDATE scans SET status='FAILED',summary=? WHERE status='RUNNING'",
                        (json.dumps({"diagnostic_codes": ["INTERRUPTED_SCAN"]}),),
                    )
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def start(self, scan_id: str) -> None:
        with self.db:
            self.db.execute("INSERT INTO scans VALUES(?,?,?)", (scan_id, "RUNNING", "{}"))

    def finish(
        self,
        summary: dict[str, Any],
        findings: Sequence[Finding] = (),
        refs: Sequence[tuple[str, str, str, int]] = (),
    ) -> None:
        with self.db:
            self.db.executemany(
                "INSERT INTO findings VALUES(?,?,?)",
                [(summary["scan_id"], f.id, f.model_dump_json()) for f in findings],
            )
            self.db.executemany(
                "INSERT INTO artifact_refs VALUES(?,?,?,?,?)",
                [(summary["scan_id"], *r) for r in refs],
            )
            self.db.execute(
                "UPDATE scans SET status=?,summary=? WHERE scan_id=?",
                (summary["status"], json.dumps(summary), summary["scan_id"]),
            )

    def get(self, scan_id: str) -> dict[str, Any] | None:
        row = self.db.execute(
            "SELECT status,summary FROM scans WHERE scan_id=?", (scan_id,)
        ).fetchone()
        if row is None:
            return None
        summary: dict[str, Any] = json.loads(row[1])
        summary.update(scan_id=scan_id, status=row[0])
        summary["artifacts"] = [
            dict(zip(("kind", "path", "sha256", "size"), r))
            for r in self.db.execute(
                "SELECT kind,path,sha256,size FROM artifact_refs WHERE scan_id=?", (scan_id,)
            )
        ]
        return summary

    def close(self) -> None:
        self.db.close()
