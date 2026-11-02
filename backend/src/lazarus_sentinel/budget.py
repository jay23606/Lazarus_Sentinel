"""Transactional, fail-closed demo budget shared by all provider invocations."""

from __future__ import annotations

import math
import sqlite3
from pathlib import Path
from uuid import uuid4

from .intake import reject_symlink_components

# Verified 2026-11-02: https://dev.meta.ai/docs/pricing-rate-limits
# Standard muse-spark-1.3 uncached prices. Integer units are micro-USD.
INPUT_MICRO_USD_PER_TOKEN = 1.25
OUTPUT_MICRO_USD_PER_TOKEN = 4.25
MAX_BUDGET = 3_000_000
MAX_ATTEMPTS = 5
OUTPUT_TOKENS = 1024


class Budget:
    def __init__(self, path: Path):
        self.path = path
        for suffix in ("", "-journal", "-wal", "-shm"):
            reject_symlink_components(Path(str(path) + suffix))
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        # Never replace an existing ledger or reconcile reservations automatically.
        with sqlite3.connect(path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS attempts (id TEXT PRIMARY KEY, reserved INTEGER NOT NULL, actual INTEGER, state TEXT NOT NULL)"
            )

    def reserve(self, request_bytes: int) -> str:
        if type(request_bytes) is not int or not 0 < request_bytes <= 16384:
            raise ValueError("UNBOUNDED_REQUEST")
        # One token per request UTF-8 byte, plus 4096 framing tokens and 2x margin.
        reservation = max(
            100_000,
            math.ceil(
                2
                * (
                    (request_bytes + 4096) * INPUT_MICRO_USD_PER_TOKEN
                    + OUTPUT_TOKENS * OUTPUT_MICRO_USD_PER_TOKEN
                )
            ),
        )
        reject_symlink_components(self.path)
        with sqlite3.connect(self.path, timeout=5) as db:
            db.execute("BEGIN IMMEDIATE")
            rows = db.execute("SELECT reserved,actual,state FROM attempts").fetchall()
            if any(
                type(row[0]) is not int
                or not 100_000 <= row[0] <= MAX_BUDGET
                or (row[2] == "SETTLED" and (type(row[1]) is not int or not 0 <= row[1] <= row[0]))
                for row in rows
            ):
                raise ValueError("INVALID_BUDGET_LEDGER")
            if any(row[2] != "SETTLED" for row in rows):
                raise ValueError("BUDGET_RECONCILIATION_REQUIRED")
            if len(rows) >= MAX_ATTEMPTS or sum(row[1] for row in rows) + reservation > MAX_BUDGET:
                raise ValueError("BUDGET_EXHAUSTED")
            identity = str(uuid4())
            db.execute("INSERT INTO attempts VALUES(?,?,NULL,'RESERVED')", (identity, reservation))
        return identity

    def settle(self, identity: str, input_tokens: int, output_tokens: int) -> None:
        if (
            type(input_tokens) is not int
            or type(output_tokens) is not int
            or input_tokens < 1
            or not 0 <= output_tokens <= OUTPUT_TOKENS
        ):
            raise ValueError("UNVERIFIABLE_USAGE")
        actual = math.ceil(
            input_tokens * INPUT_MICRO_USD_PER_TOKEN + output_tokens * OUTPUT_MICRO_USD_PER_TOKEN
        )
        reject_symlink_components(self.path)
        with sqlite3.connect(self.path, timeout=5) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT reserved,state FROM attempts WHERE id=?", (identity,)
            ).fetchone()
            if row is None or row[1] != "RESERVED" or actual > row[0]:
                raise ValueError("UNVERIFIABLE_USAGE")
            db.execute(
                "UPDATE attempts SET actual=?,state='SETTLED' WHERE id=?", (actual, identity)
            )
