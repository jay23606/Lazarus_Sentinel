"""Minimal fixture-only CLI; errors never echo untrusted arguments."""

import argparse
import json
from collections.abc import Sequence
from typing import NoReturn
from uuid import uuid4

from .service import scan


class SafeParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ValueError("INVALID_ARGUMENTS")


def main(argv: Sequence[str] | None = None) -> int:
    parser = SafeParser(prog="lazarus")
    commands = parser.add_subparsers(dest="command", required=True)
    scan_parser = commands.add_parser("scan")
    scan_parser.add_argument("--target", required=True)
    try:
        args = parser.parse_args(argv)
        summary = scan(args.target)
    except ValueError:
        summary = {
            "scan_id": str(uuid4()),
            "status": "FAILED",
            "artifact_dir": None,
            "counts": {},
            "diagnostic_codes": ["INVALID_ARGUMENTS"],
        }
    except Exception:  # noqa: BLE001 - final CLI boundary must never expose untrusted exception text.
        summary = {
            "scan_id": str(uuid4()),
            "status": "FAILED",
            "artifact_dir": None,
            "counts": {},
            "diagnostic_codes": ["INTERNAL_ERROR"],
        }
    print(json.dumps(summary, sort_keys=True))
    return {"COMPLETED": 0, "PARTIAL": 2, "FAILED": 1}[summary["status"]]
