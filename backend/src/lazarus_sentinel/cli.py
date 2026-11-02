"""Minimal fixture-only CLI; errors never echo untrusted arguments."""

import argparse
import json
import re
from collections.abc import Sequence
from typing import NoReturn
from uuid import uuid4

from .bundle import export_demo_bundle
from .explanations import explain_finding
from .service import scan

SAFE_CODES = frozenset(
    [
        "INVALID_ARGUMENTS",
        "INVALID_UUID",
        "INVALID_PROVIDER",
        "FINDING_NOT_FOUND",
        "CONTEXT_SIZE_LIMIT",
        "ANNOTATION_BINDING_MISMATCH",
        "ANNOTATION_REQUEST_MISMATCH",
        "INVALID_CITATIONS",
        "ANNOTATION_SIZE_LIMIT",
        "ANNOTATION_ID_MISMATCH",
        "STALE_GRAPH",
        "INVALID_ARTIFACT_SIZE",
        "DUPLICATE_JSON_KEYS",
        "INVALID_JSON_CONSTANT",
        "GRAPH_LIMIT",
        "DUPLICATE_FINDING_IDS",
        "SCAN_NOT_COMMITTED",
        "INVALID_COMMITTED_REFERENCES",
        "INVALID_COMMITTED_REFERENCE",
        "ARTIFACT_HASH_MISMATCH",
        "ARTIFACT_MIRROR_MISMATCH",
        "SUMMARY_MIRROR_MISMATCH",
        "BUNDLE_FILES_MISMATCH",
        "BUNDLE_SIZE_LIMIT",
        "BUNDLE_HASH_MISMATCH",
        "BUNDLE_REVISION_MISMATCH",
        "BUNDLE_STATUS_MISMATCH",
        "META_KEY_MISSING",
        "INVALID_META_REQUEST",
        "META_TRANSPORT_FAILED",
        "META_RESPONSE_LIMIT",
        "META_DEADLINE_EXCEEDED",
        "META_UNEXPECTED_TOOLS",
        "UNBOUNDED_REQUEST",
        "INVALID_BUDGET_LEDGER",
        "BUDGET_RECONCILIATION_REQUIRED",
        "BUDGET_EXHAUSTED",
        "UNVERIFIABLE_USAGE",
    ]
)


def safe_error_code(error: ValueError) -> str:
    # Only explicitly reviewed constants may cross the CLI boundary.
    code = error.args[0] if len(error.args) == 1 else None
    if type(code) is str and re.fullmatch(r"[A-Z][A-Z0-9_]{0,63}", code) and code in SAFE_CODES:
        return code
    return "INTERNAL_ERROR"


class SafeParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ValueError("INVALID_ARGUMENTS")


def main(argv: Sequence[str] | None = None) -> int:
    parser = SafeParser(prog="lazarus")
    commands = parser.add_subparsers(dest="command", required=True)
    scan_parser = commands.add_parser("scan")
    scan_parser.add_argument("--target", required=True)
    demo_parser = commands.add_parser("demo")
    demo_commands = demo_parser.add_subparsers(dest="demo_command", required=True)
    export_parser = demo_commands.add_parser("export")
    export_parser.add_argument("--scan-id", required=True)
    export_parser.add_argument("--annotation-id")
    explain_parser = commands.add_parser("explain")
    explain_parser.add_argument("--scan-id", required=True)
    explain_parser.add_argument("--finding-id", required=True)
    explain_parser.add_argument(
        "--provider", choices=("disabled", "mock", "meta"), default="disabled"
    )
    try:
        args = parser.parse_args(argv)
        if args.command == "scan":
            summary = scan(args.target)
        elif args.command == "demo":
            summary = export_demo_bundle(args.scan_id, args.annotation_id)
        else:
            summary = explain_finding(args.scan_id, args.finding_id, args.provider)
    except ValueError as error:
        summary = {
            "scan_id": str(uuid4()),
            "status": "FAILED",
            "artifact_dir": None,
            "counts": {},
            "diagnostic_codes": [safe_error_code(error)],
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
    return {"COMPLETED": 0, "EXPORTED": 0, "RECORDED": 0, "DISABLED": 0, "PARTIAL": 2, "FAILED": 1}[
        summary["status"]
    ]
