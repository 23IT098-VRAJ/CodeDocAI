import contextlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

from git import GitCommandError, Repo

MAX_REPO_SIZE_MB = 100
MAX_PY_FILES = 500
MAX_ARCHIVE_ENTRIES = 20000
STALE_SCAN_HOURS = 6
# GitHub reports the size of the whole history, which is larger than the shallow clone,
# so the pre-check only refuses repositories far past the real limit.
MAX_REMOTE_SIZE_MB = 10 * MAX_REPO_SIZE_MB
CLONE_TIMEOUT_SECONDS = 180  # not supported by GitPython on Windows; the low-speed limit still applies

# Every scan directory is created with this prefix; cleanup_repo refuses anything else.
TEMP_PREFIX = "codedocai_scan_"

_GITHUB_URL_RE = re.compile(r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?(?:\.git)?/?$")
_SKIPPED_DIRS = {"venv", ".venv", "__pycache__", "site-packages", "tests", "test"}

class RepoValidationError(Exception):
    """Raised when a repository violates size or file count constraints."""

def _get_dir_size_mb(directory: Path) -> float:
    """Calculates the total size of a directory in megabytes."""
    total_bytes = sum(f.stat().st_size for f in directory.rglob('*') if f.is_file() and not f.is_symlink())
    return total_bytes / (1024 * 1024)

def _is_skipped(rel_path: Path) -> bool:
    """
    True for files the scan ignores: hidden folders (e.g. .git), virtualenvs, caches,
    test directories, test modules and __init__.py. Only the path inside the
    repository is inspected, never the folder the repository happens to live in.
    """
    if any(part.startswith('.') or part in _SKIPPED_DIRS for part in rel_path.parts[:-1]):
        return True
    name = rel_path.name
    return (
        name.startswith(('.', "test_"))
        or name in ("__init__.py", "conftest.py")
        or name.endswith("_test.py")
    )

def has_byte_order_mark(path: str | Path) -> bool:
    """True when the file starts with a UTF-8 byte-order mark, which read_source removes."""
    with Path(path).open("rb") as handle:
        return handle.read(3) == b"\xef\xbb\xbf"


def read_source(path: str | Path) -> str:
    """
    A scanned file's text exactly as saved: a byte-order mark is dropped, line endings
    are kept. Path.read_text would turn CRLF into LF, and the documented copy and the
    patch would then no longer match a file saved with Windows line endings.
    """
    return Path(path).read_bytes().decode("utf-8-sig", errors="replace")


def _is_inside(file: Path, root: Path) -> bool:
    """
    False for a symlink, or a file reached through a symlinked folder, that points
    outside the repository. A cloned repo could otherwise make the scan read, index
    and send to the cloud a file such as ~/.env.
    """
    if file.is_symlink():
        return False
    try:
        return file.resolve().is_relative_to(root.resolve())
    except OSError:
        return False


def validate_github_url(repo_url: str) -> str:
    """Accepts only the root HTTPS URL of a GitHub repository. Returns the cleaned URL."""
    url = (repo_url or "").strip()
    if not _GITHUB_URL_RE.match(url):
        raise RepoValidationError(
            "Enter the root HTTPS URL of a public GitHub repository, "
            "for example https://github.com/owner/repository"
        )
    return url

def validate_repository(repo_path: str | Path) -> list[str]:
    """
    Validates repository against size and file-count caps.
    Returns a list of relative paths to all Python files found.
    """
    path = Path(repo_path)
    if not path.is_dir():
        raise RepoValidationError(f"Invalid directory path: {repo_path}")

    # Check total size
    total_size_mb = _get_dir_size_mb(path)
    if total_size_mb > MAX_REPO_SIZE_MB:
        raise RepoValidationError(
            f"Repository size ({total_size_mb:.1f}MB) exceeds the {MAX_REPO_SIZE_MB}MB limit."
        )

    py_files = sorted(
        str(f.relative_to(path))
        for f in path.rglob('*.py')
        if _is_inside(f, path) and f.is_file() and not _is_skipped(f.relative_to(path))
    )

    if not py_files:
        raise RepoValidationError(
            "This repository has no Python files to document. Tests, virtual environments and "
            "hidden folders are skipped, so check the code isn't only in those."
        )
    if len(py_files) > MAX_PY_FILES:
        raise RepoValidationError(
            f"Repository contains {len(py_files)} Python files, exceeding the {MAX_PY_FILES} limit."
        )

    return py_files

def _remote_size_mb(repo_url: str) -> float | None:
    """
    The size GitHub reports for a repository, in MB, or None when it can't be found
    out (no network, API rate limit, private repo). Used to refuse a huge repository
    before downloading it, instead of after.
    """
    owner_repo = repo_url.removeprefix("https://github.com/").removesuffix("/").removesuffix(".git")
    request = urllib.request.Request(
        f"https://api.github.com/repos/{owner_repo}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "CodeDocAI"},
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            size_kb = json.load(response).get("size")
    except (OSError, ValueError):
        return None
    return size_kb / 1024 if isinstance(size_kb, (int, float)) else None


def clone_github_repo(repo_url: str, target_dir: str | Path) -> dict:
    """
    Performs a shallow clone of a public GitHub repository.
    Returns metadata matching the st.session_state['repo_source'] schema.
    """
    repo_url = validate_github_url(repo_url)
    remote_mb = _remote_size_mb(repo_url)
    if remote_mb is not None and remote_mb > MAX_REMOTE_SIZE_MB:
        raise RepoValidationError(
            f"GitHub reports this repository at {remote_mb:.0f}MB, far past the {MAX_REPO_SIZE_MB}MB limit, "
            "so it was not downloaded."
        )

    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)

    try:
        # Enforce shallow clone (depth=1) for minimal memory footprint
        repo = Repo.clone_from(
            repo_url,
            target_path,
            depth=1,
            env={
                # A private or missing repository must fail, not wait for a password prompt.
                "GIT_TERMINAL_PROMPT": "0",
                "GCM_INTERACTIVE": "never",
                # Abort a transfer that stays below 1 KB/s for 30 s (works on every OS).
                "GIT_HTTP_LOW_SPEED_LIMIT": "1000",
                "GIT_HTTP_LOW_SPEED_TIME": "30",
            },
            **({} if os.name == "nt" else {"kill_after_timeout": CLONE_TIMEOUT_SECONDS}),
        )
        repo.close()  # release file handles so the folder can be deleted on Windows
    except GitCommandError as error:
        raise RuntimeError(f"Git clone failed: {error.stderr.strip() if error.stderr else error}") from error

    py_files = validate_repository(target_path)

    return {
        "type": "github",
        "value": repo_url,
        "local_path": str(target_path),
        "py_files": py_files
    }

def _check_archive(archive: zipfile.ZipFile) -> None:
    """
    Refuses an archive before anything is written to disk if it would unpack to more
    than the repository limits. A few kilobytes of zip can otherwise expand to
    gigabytes (a "zip bomb"); the sizes checked here are the ones extraction enforces.
    """
    entries = archive.infolist()
    if len(entries) > MAX_ARCHIVE_ENTRIES:
        raise RepoValidationError(
            f"Archive contains {len(entries)} entries, exceeding the {MAX_ARCHIVE_ENTRIES} limit."
        )
    unpacked_mb = sum(entry.file_size for entry in entries) / (1024 * 1024)
    if unpacked_mb > MAX_REPO_SIZE_MB:
        raise RepoValidationError(
            f"Archive unpacks to {unpacked_mb:.1f}MB, exceeding the {MAX_REPO_SIZE_MB}MB limit."
        )

def extract_zip(zip_source: str | Path | bytes, target_dir: str | Path) -> dict:
    """
    Extracts a zip archive to the target directory and validates contents.
    Returns metadata matching the st.session_state['repo_source'] schema.
    """
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_source, 'r') as archive:
            _check_archive(archive)
            archive.extractall(target_path)
    except zipfile.BadZipFile as error:
        raise ValueError("The provided file is not a valid zip archive.") from error

    py_files = validate_repository(target_path)

    return {
        "type": "zip",
        "value": getattr(zip_source, 'name', str(zip_source)),
        "local_path": str(target_path),
        "py_files": py_files
    }

def _force_remove(func, path, _exc):
    """rmtree handler: git marks its object files read-only, which blocks deletion on Windows."""
    with contextlib.suppress(OSError):
        Path(path).chmod(stat.S_IWRITE)
        func(path)

def cleanup_repo(local_path: str | Path | None) -> bool:
    """
    Deletes a scan directory created by this app. Returns True if it is gone.
    Paths that were not created with TEMP_PREFIX are left untouched.
    """
    if not local_path:
        return False
    path = Path(local_path)
    if not path.name.startswith(TEMP_PREFIX):
        return False
    if path.exists():
        if sys.version_info >= (3, 12):
            shutil.rmtree(path, onexc=_force_remove)
        else:
            shutil.rmtree(path, onerror=_force_remove)
    return not path.exists()

def sweep_stale_scans(max_age_hours: float = STALE_SCAN_HOURS, temp_root: str | Path | None = None) -> int:
    """
    Deletes scan directories left behind by sessions that ended without cleaning up
    (a closed browser tab, a crash). Only folders created with TEMP_PREFIX and not
    modified for max_age_hours are removed, so a scan in progress is never touched.
    Returns how many were deleted.
    """
    root = Path(temp_root) if temp_root else Path(tempfile.gettempdir())
    cutoff = time.time() - max_age_hours * 3600
    removed = 0
    try:
        candidates = list(root.glob(TEMP_PREFIX + "*"))
    except OSError:
        return 0
    for path in candidates:
        # One unreadable folder must not stop the rest of the sweep.
        with contextlib.suppress(OSError):
            if path.is_dir() and path.stat().st_mtime < cutoff and cleanup_repo(path):
                removed += 1
    return removed
