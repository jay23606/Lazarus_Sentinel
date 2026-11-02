"""Explicit, bounded standard Meta transport. No retries, redirects, or error bodies."""

from __future__ import annotations

import http.client
import multiprocessing
import os
import sys
import time
from multiprocessing.connection import Connection
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    if sys.platform == "win32":
        from multiprocessing.context import SpawnContext as TransportContext
    else:
        from multiprocessing.context import ForkContext as TransportContext

from .budget import Budget
from .bundle import canonical_bytes, parse_json

DEADLINE_SECONDS = 20.0
MAX_RESPONSE_BYTES = 32768


def _transport(payload: bytes, key: str) -> dict[str, Any]:
    connection = http.client.HTTPSConnection("api.meta.ai", timeout=DEADLINE_SECONDS)
    try:
        connection.request(
            "POST",
            "/v1/chat/completions",
            body=payload,
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        )
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError("META_TRANSPORT_FAILED")
        data = response.read(MAX_RESPONSE_BYTES + 1)
        if len(data) > MAX_RESPONSE_BYTES:
            raise ValueError("META_RESPONSE_LIMIT")
        parsed = parse_json(data)
        if not isinstance(parsed, dict):
            raise TypeError("META_INVALID_RESPONSE")
        return parsed
    finally:
        connection.close()


def _child(pipe: Connection, payload: bytes, key: str) -> None:
    try:
        result = canonical_bytes(_transport(payload, key))
        if len(result) > MAX_RESPONSE_BYTES:
            raise ValueError("META_RESPONSE_LIMIT")
        pipe.send_bytes(b"O" + result)
    except BaseException:  # noqa: BLE001 - child boundary must redact all failures
        # Provider exceptions may carry credentials, prompts or remote bodies.
        pipe.send_bytes(b"E")
    finally:
        pipe.close()


def bounded_transport(payload: bytes, key: str) -> dict[str, Any]:
    context = cast(
        "TransportContext",
        multiprocessing.get_context("spawn" if sys.platform == "win32" else "fork"),
    )
    reader, writer = context.Pipe(duplex=False)
    process = context.Process(target=_child, args=(writer, payload, key), daemon=True)
    deadline = time.monotonic() + DEADLINE_SECONDS
    process.start()
    writer.close()
    try:
        if not reader.poll(max(0, deadline - time.monotonic())):
            raise ValueError("META_DEADLINE_EXCEEDED")
        try:
            data = reader.recv_bytes(MAX_RESPONSE_BYTES + 1)
        except (EOFError, OSError):
            raise ValueError("META_TRANSPORT_FAILED") from None
        if not data.startswith(b"O"):
            raise ValueError("META_TRANSPORT_FAILED")
        result = parse_json(data[1:])
        if not isinstance(result, dict):
            raise TypeError("META_INVALID_RESPONSE")
        return result
    finally:
        reader.close()
        if process.is_alive():
            process.kill()
        process.join(timeout=1)
        process.close()


def generate(payload: bytes, ledger_path: Path) -> dict[str, Any]:
    key = os.environ.get("MODEL_API_KEY")
    if not key:
        raise ValueError("META_KEY_MISSING")
    request = parse_json(payload)
    if (
        len(payload) > 16384
        or request.get("model") != "muse-spark-1.3"
        or request.get("max_completion_tokens") != 1024
        or request.get("stream") is not False
        or set(request)
        != {"model", "messages", "max_completion_tokens", "response_format", "stream"}
    ):
        raise ValueError("INVALID_META_REQUEST")
    budget = Budget(ledger_path)
    attempt = budget.reserve(len(payload))
    result = bounded_transport(payload, key)
    usage = result.get("usage")
    if not isinstance(usage, dict):
        raise TypeError("UNVERIFIABLE_USAGE")
    input_tokens, output_tokens = usage.get("prompt_tokens"), usage.get("completion_tokens")
    if type(input_tokens) is not int or type(output_tokens) is not int:
        raise ValueError("UNVERIFIABLE_USAGE")
    if "total_tokens" in usage and (
        type(usage["total_tokens"]) is not int
        or usage["total_tokens"] != input_tokens + output_tokens
    ):
        raise ValueError("UNVERIFIABLE_USAGE")
    budget.settle(attempt, input_tokens, output_tokens)
    try:
        choice = result["choices"][0]
        message = choice["message"]
        if (
            choice.get("finish_reason") == "tool_calls"
            or message.get("tool_calls")
            or message.get("function_call")
        ):
            raise ValueError("META_UNEXPECTED_TOOLS")
        content = message["content"]
        if not isinstance(content, str) or len(content.encode()) > MAX_RESPONSE_BYTES:
            raise TypeError("META_INVALID_RESPONSE")
        response = parse_json(content.encode())
        if not isinstance(response, dict):
            raise TypeError("META_INVALID_RESPONSE")
        return response
    except (KeyError, IndexError, TypeError):
        raise TypeError("META_INVALID_RESPONSE") from None
