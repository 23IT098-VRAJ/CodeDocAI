import os
import shutil
import zipfile
import tempfile
from pathlib import Path
from git import Repo, GitCommandError

MAX_REPO_SIZE_MB = 100
MAX_PY_FILES = 500

class RepoValidationError(Exception):
    """Raised when a repository violates size or file count constraints."""
    pass

def _get_dir_size_mb(directory: Path) -> float:
    """Calculates the total size of a directory in megabytes."""
    total_bytes = sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())
    return total_bytes / (1024 * 1024)

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

    # Collect Python files, ignoring hidden folders (e.g., .git) and virtualenvs
    py_files = [
        str(f.relative_to(path))
        for f in path.rglob('*.py')
        if not any(part.startswith('.') or part in ('venv', '.venv', '__pycache__', 'site-packages')
                   for part in f.parts)
    ]

    if len(py_files) > MAX_PY_FILES:
        raise RepoValidationError(
            f"Repository contains {len(py_files)} Python files, exceeding the {MAX_PY_FILES} limit."
        )

    return py_files

def clone_github_repo(repo_url: str, target_dir: str | Path) -> dict:
    """
    Performs a shallow clone of a public GitHub repository.
    Returns metadata matching the st.session_state['repo_source'] schema.
    """
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)

    try:
        # Enforce shallow clone (depth=1) for minimal memory footprint
        Repo.clone_from(repo_url, target_path, depth=1)
    except GitCommandError as e:
        raise RuntimeError(f"Git clone failed: {e.stderr.strip() if e.stderr else str(e)}")

    py_files = validate_repository(target_path)

    return {
        "type": "github",
        "value": repo_url,
        "local_path": str(target_path),
        "py_files": py_files
    }

def extract_zip(zip_source: str | Path | bytes, target_dir: str | Path) -> dict:
    """
    Extracts a zip archive to the target directory and validates contents.
    Returns metadata matching the st.session_state['repo_source'] schema.
    """
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_source, 'r') as archive:
            archive.extractall(target_path)
    except zipfile.BadZipFile:
        raise ValueError("The provided file is not a valid zip archive.")

    py_files = validate_repository(target_path)

    return {
        "type": "zip",
        "value": getattr(zip_source, 'name', str(zip_source)),
        "local_path": str(target_path),
        "py_files": py_files
    }

# --- Built-in Test Block ---
if __name__ == "__main__":
    import io

    print("=== Testing Zip Extraction & Validation ===")
    # 1. Create a dummy in-memory zip containing two python files
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr("module_a.py", "def add(a, b):\n    return a + b\n")
        zf.writestr("subpkg/module_b.py", "def sub(a, b):\n    return a - b\n")
        zf.writestr("README.md", "# Test Repo\n")
    zip_buffer.seek(0)

    test_dir = tempfile.mkdtemp(prefix="codedocai_test_")
    try:
        result = extract_zip(zip_buffer, test_dir)
        print("Extraction Result:")
        print(f"  Type: {result['type']}")
        print(f"  Local Path: {result['local_path']}")
        print(f"  Python Files Found ({len(result['py_files'])}): {result['py_files']}")
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)
        print("Temporary test directory cleaned up.")