"""Bounded manifest-only intake; never imports or executes a target file."""

from __future__ import annotations

import base64
import hashlib
import json
import ntpath
import os
import stat
import sys
from pathlib import Path, PurePosixPath

from pydantic import ValidationError

from .models import SecurityPolicy, Snapshot, stable_id

MAX_FILES = 100
MAX_FILE_BYTES = 256 * 1024
MAX_TOTAL_BYTES = 5 * 1024 * 1024
MAX_METADATA_BYTES = 64 * 1024


class ScanError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _path(value: str) -> list[str]:
    path = PurePosixPath(value)
    if (
        not value
        or len(value) > 240
        or "\\" in value
        or "\x00" in value
        or ":" in value
        or path.is_absolute()
        or str(path) != value
        or any(part in {".", ".."} or ntpath.isreserved(part) for part in path.parts)
    ):
        raise ScanError("INVALID_PATH")
    return list(path.parts)


def _absolute_parts(path: Path) -> tuple[str, ...]:
    if ".." in path.parts:
        raise ScanError("INVALID_PATH")
    return path.absolute().parts


def reject_symlink_components(path: Path) -> None:
    """Reject existing lexical symlinks; this precheck is not a hostile-FS sandbox."""
    parts = _absolute_parts(path)
    current = Path(parts[0])
    try:
        for part in ("", *parts[1:]):
            current /= part
            try:
                metadata = current.lstat()
            except FileNotFoundError:
                return
            if (
                stat.S_ISLNK(metadata.st_mode)
                or getattr(metadata, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
            ):
                raise ScanError("SYMLINK_PATH")
    except OSError:
        raise ScanError("UNREADABLE_PATH") from None


def _open_root(root: Path) -> int:
    if sys.platform == "win32":
        raise ScanError("UNSUPPORTED_POSIX_READER")
    parts = _absolute_parts(root)
    descriptor = os.open(parts[0], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[1:]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _exact_component(directory: int, component: str) -> None:
    found = False
    with os.scandir(directory) as entries:
        for count, entry in enumerate(entries, 1):
            if count > 200:
                raise ScanError("DIRECTORY_ENTRY_LIMIT")
            found = found or entry.name == component
    if not found:
        raise ScanError("PATH_ALIAS")


def _identity(metadata: os.stat_result) -> tuple[int, int, int, int]:
    return metadata.st_dev, metadata.st_ino, metadata.st_size, metadata.st_mtime_ns


def _read_windows(root: Path, name: str, limit: int) -> bytes:
    """Fixed-fixture reader; prechecks do not provide hostile-filesystem isolation."""
    parts = _path(name)
    current = root
    try:
        reject_symlink_components(root)
        for part in parts:
            found = False
            with os.scandir(current) as entries:
                for count, entry in enumerate(entries, 1):
                    if count > 200:
                        raise ScanError("DIRECTORY_ENTRY_LIMIT")
                    found = found or entry.name == part
            if not found:
                raise ScanError("PATH_ALIAS")
            current /= part
            reject_symlink_components(current)
        before = current.lstat()
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
            raise ScanError("INVALID_FILE")
        with current.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or _identity(before) != _identity(opened):
                raise ScanError("FILE_CHANGED_OR_OVERSIZE")
            data = stream.read(limit + 1)
            after = os.fstat(stream.fileno())
        reject_symlink_components(current)
        if (
            len(data) > limit
            or _identity(before) != _identity(after)
            or _identity(before) != _identity(current.lstat())
        ):
            raise ScanError("FILE_CHANGED_OR_OVERSIZE")
        return data
    except OSError:
        raise ScanError("UNREADABLE_FILE") from None


def _read(root: Path, name: str, limit: int) -> bytes:
    if sys.platform == "win32":
        return _read_windows(root, name, limit)
    parts = _path(name)
    directory = -1
    descriptor = -1
    try:
        directory = _open_root(root)
        for part in parts[:-1]:
            _exact_component(directory, part)
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        _exact_component(directory, parts[-1])
        descriptor = os.open(
            parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
        )
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
            raise ScanError("INVALID_FILE")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = -1
            data = stream.read(limit + 1)
            after = os.fstat(stream.fileno())
        if len(data) > limit or (before.st_size, before.st_mtime_ns) != (
            after.st_size,
            after.st_mtime_ns,
        ):
            raise ScanError("FILE_CHANGED_OR_OVERSIZE")
        return data
    except OSError:
        raise ScanError("UNREADABLE_FILE") from None
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if directory >= 0:
            os.close(directory)


def load_snapshot(root: Path) -> Snapshot:
    try:
        manifest = _read(root, "manifest.json", MAX_METADATA_BYTES)
        names = json.loads(manifest)
        if (
            not isinstance(names, list)
            or not names
            or not all(isinstance(name, str) for name in names)
            or len(names) != len(set(names))
            or names.count("policy.json") != 1
        ):
            raise ScanError("INVALID_MANIFEST")
        sources = [name for name in names if name != "policy.json"]
        if len(sources) > MAX_FILES or any(not name.endswith(".py") for name in sources):
            raise ScanError("INVALID_MANIFEST")
        # Reject case aliases even on case-sensitive hosts for portable source identities.
        if len({name.casefold() for name in names}) != len(names):
            raise ScanError("PATH_ALIAS")
        policy_data = _read(root, "policy.json", MAX_METADATA_BYTES)
        policy = SecurityPolicy.model_validate_json(policy_data)
        files = {}
        hashes = {}
        total = 0
        for name in sorted(sources):
            data = _read(root, name, min(MAX_FILE_BYTES, MAX_TOTAL_BYTES - total))
            total += len(data)
            if total > MAX_TOTAL_BYTES:
                raise ScanError("TOTAL_LIMIT")
            files[name] = base64.b64encode(data).decode("ascii")
            hashes[name] = hashlib.sha256(data).hexdigest()
        policy_hash = hashlib.sha256(policy_data).hexdigest()
        return Snapshot(
            revision=stable_id(
                "revision", hashes, hashlib.sha256(manifest).hexdigest(), policy_hash
            ),
            files=files,
            file_hashes=hashes,
            manifest_base64=base64.b64encode(manifest).decode("ascii"),
            policy_base64=base64.b64encode(policy_data).decode("ascii"),
            policy_hash=policy_hash,
            policy=policy,
        )
    except (ValueError, TypeError, ValidationError, RecursionError):
        raise ScanError("INVALID_METADATA") from None


def verify_snapshot(root: Path, snapshot: Snapshot) -> None:
    if load_snapshot(root) != snapshot:
        raise ScanError("STALE_SNAPSHOT")
