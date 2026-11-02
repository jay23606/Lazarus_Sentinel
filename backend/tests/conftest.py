"""Keep symlink security tests explicit on Windows hosts without link privileges."""

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def windows_symlink_privilege(monkeypatch):
    if os.name != "nt":
        return
    original = Path.symlink_to

    def symlink(path, target, target_is_directory=False):
        try:
            original(path, target, target_is_directory=target_is_directory)
        except OSError as error:
            if error.winerror == 1314:
                pytest.skip(
                    "Windows symlink privilege unavailable; junction and reparse checks run separately"
                )
            raise

    monkeypatch.setattr(Path, "symlink_to", symlink)
