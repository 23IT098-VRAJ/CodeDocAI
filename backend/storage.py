"""
backend/storage.py
Small JSON files shared by every session (the audit log, the API cooldowns).

Each change is a read-modify-write under a lock, so two sessions writing at the same
moment can't drop each other's entries, and the file is replaced in one step, so a
reader never sees half a file. The lock covers the threads of one server process,
which is how Streamlit runs.
"""
import contextlib
import json
import logging
import os
import tempfile
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


def _lock_for(path: Path) -> threading.Lock:
    key = str(Path(path).resolve())
    with _locks_guard:
        return _locks.setdefault(key, threading.Lock())


def read_json(path: str | Path, default: Any) -> Any:
    """The file's content, or `default` when it is missing, unreadable or of another type."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default
    return data if isinstance(data, type(default)) else default


def _write_atomic(path: Path, data: Any) -> None:
    text = json.dumps(data, indent=2)
    handle, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as temp:
            temp.write(text)
        # Synced folders (OneDrive, Dropbox) can hold the target open for a moment.
        for _ in range(9):
            with contextlib.suppress(PermissionError):
                Path(temp_name).replace(path)
                return
            time.sleep(0.1)
        Path(temp_name).replace(path)  # last try; its error reaches the caller
    finally:
        if Path(temp_name).exists():
            Path(temp_name).unlink(missing_ok=True)


def update_json(path: str | Path, change: Callable[[Any], Any], default: Any) -> Any:
    """
    Reads the file, applies `change` to its content and writes the result back, all
    under the file's lock. Returns the new content. A failed write is logged and the
    new content is still returned, so callers never crash on a full or locked disk.
    """
    path = Path(path)
    with _lock_for(path):
        new = change(read_json(path, default))
        try:
            _write_atomic(path, new)
        except OSError as error:
            logger.warning("Could not write %s: %s", path.name, error)
        return new
