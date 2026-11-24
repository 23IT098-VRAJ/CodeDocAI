"""
backend/pipeline.py
Core pipeline orchestrator integrating AST extraction, local CodeT5 Engine,
CrewAI agents, and ChromaDB indexing.

The pipeline is UI-independent: it receives everything it needs as arguments and
reports back through the events it yields.

Events
    {"type": "progress", "function": str, "status": str}
    {"type": "result", "function": str, "docstring": str, "file": str}
    {"type": "partial", "data": dict, "overview_context": str}   local work is saved
    {"type": "done", "overview": str, "overview_status": "ok", "functions": list,
     "coverage": dict, "documented_files": {path: source}, "patch": str}
    {"type": "rate_limited", "message": str}                     overview failed
    {"type": "error", "message": str}

Vector index
    One entry per function or method (kind "function"), one per class (kind "class"),
    one per file (kind "file") and, once the overview exists, one for the overview
    itself (kind "overview").

Classes are extracted, indexed and counted, but their docstrings are not drafted:
the local model is trained on functions and describes classes poorly.
"""

import contextlib
import json
import logging
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from backend.agents.explainer import generate_repository_overview
from backend.coverage import build_coverage
from backend.model.summarizer import summarize_batch
from backend.outline import file_outline, repository_outline
from backend.parser.extractor import extract_definitions, extract_module_docstring
from backend.rag.vectorstore import add_documents, reset_collection
from backend.repo.loader import has_byte_order_mark, read_source
from backend.writer import insert_docstrings, make_patch

logger = logging.getLogger(__name__)

# Lock the cache path strictly to the project root
_ROOT_DIR = Path(__file__).resolve().parents[1]
_CACHE_PATH = _ROOT_DIR / "docs_cache.json"
_DISK_CACHE_ENV = "CODEDOCAI_DISK_CACHE"

# Local CodeT5 inference: functions per model call.
LOCAL_BATCH_SIZE = 8
# At most this many docstrings are drafted per scan (roughly 3-5 minutes on a CPU), so a huge
# repository can't hold the screen for an hour. The rest stay missing; nothing extra goes to the cloud.
MAX_LOCAL_DRAFTS = 1000

# Long functions get extra index entries for the rest of their source: the embedding model only
# reads about the first 256 tokens of an entry, so code further down was invisible to search.
INDEX_PART_CHARS = 1500
MAX_INDEX_PARTS = 4

# Cloud fallback budget: at most CLOUD_BATCH_SIZE * MAX_CLOUD_BATCHES functions
# are sent to the cloud per scan, in MAX_CLOUD_BATCHES requests.
CLOUD_BATCH_SIZE = 8
MAX_CLOUD_BATCHES = 5

OVERVIEW_DOC_ID = "overview"
OVERVIEW_SKIPPED_MESSAGE = (
    "No architecture overview yet: the cloud models didn’t answer. "
    "Open the Generate step and retry; the docstrings below are unaffected."
)


def disk_cache_enabled() -> bool:
    """
    Off by default: results then live only in the browser session, so no scanned
    source is left on disk and no session can load another session’s results.
    Set CODEDOCAI_DISK_CACHE=1 on a single-user machine to make the last scan
    survive a page refresh.
    """
    return os.environ.get(_DISK_CACHE_ENV, "").strip().lower() in ("1", "true", "yes", "on")


def save_results_cache(data: dict[str, Any]) -> None:
    if not disk_cache_enabled():
        return
    try:
        Path(_CACHE_PATH).write_text(json.dumps(data), encoding="utf-8")
    except (OSError, TypeError, ValueError) as error:
        logger.warning("Could not write the results cache: %s", error)


def load_results_cache() -> dict[str, Any] | None:
    """The last saved scan, or None when the disk cache is off, missing or unreadable."""
    if not disk_cache_enabled():
        return None
    try:
        data = json.loads(Path(_CACHE_PATH).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def generate_overview(overview_context: str) -> str:
    """One cloud request for the repository overview. Raises if the cloud is unreachable."""
    return generate_repository_overview(overview_context)


def index_overview(overview: str, collection_name: str | None = None) -> None:
    """Adds the overview to the vector index so broad questions have something to retrieve."""
    add_documents(
        documents=[f"Repository overview\n{overview}"],
        metadatas=[{"kind": "overview", "file": "", "function": ""}],
        ids=[OVERVIEW_DOC_ID],
        collection_name=collection_name,
    )


def _local_docstring(ai_engine: Any, fn_source: str) -> str | None:
    """Drafts a docstring with the local CodeT5 engine. Returns None if it cannot."""
    if not ai_engine or not fn_source.strip():
        return None
    try:
        import torch

        tokenizer, model, device = ai_engine

        # Apply identical inference constraints as the benchmark
        inputs = tokenizer(fn_source, max_length=384, truncation=True, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=64,
                num_beams=4,
                no_repeat_ngram_size=3,
                early_stopping=True,
            )
        return tokenizer.decode(outputs[0], skip_special_tokens=True).strip() or None
    except Exception as error:  # noqa: BLE001 - any model failure means "no draft", never a crashed scan
        logger.warning("Local CodeT5 generation failed: %s", error)
        return None


def _local_docstrings(ai_engine: Any, sources: list[str]) -> list[str | None]:
    """
    Drafts one docstring per source in a single model call. The result is the same
    as calling _local_docstring for each source, only faster. If the batched call
    fails, each source is tried on its own.
    """
    if not ai_engine:
        return [None] * len(sources)
    try:
        import torch

        tokenizer, model, device = ai_engine

        inputs = tokenizer(sources, max_length=384, truncation=True, padding=True, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=64,
                num_beams=4,
                no_repeat_ngram_size=3,
                early_stopping=True,
            )
        decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        return [text.strip() or None for text in decoded]
    except Exception as error:  # noqa: BLE001 - fall back to one function at a time
        logger.warning("Batched CodeT5 generation failed (%s); drafting one function at a time.", error)
        return [_local_docstring(ai_engine, source) for source in sources]


def _build_index_entries(files: list[dict]) -> tuple[list, list, list]:
    """Documents, metadata and ids for every function, class and file."""
    documents, metadatas, ids = [], [], []

    doc_id = 0
    for file_info in files:
        for fn in file_info["functions"]:
            is_class = fn.get("kind") == "class"
            documents.append(
                f"File: {fn.get('file', '')}\n"
                f"{'Class' if is_class else 'Function'}: {fn.get('name', 'unknown')}\n"
                f"Docstring: {fn['docstring'] or '(none)'}\n"
                f"Source:\n{fn['source']}"
            )
            metadatas.append({
                "kind": "class" if is_class else "function",
                "file": fn.get("file", ""),
                "function": fn.get("name", "unknown"),
            })
            ids.append(f"doc_{doc_id}")
            source = fn.get("source") or ""
            for part in range(1, MAX_INDEX_PARTS):
                piece = source[part * INDEX_PART_CHARS:(part + 1) * INDEX_PART_CHARS]
                if not piece.strip():
                    break
                documents.append(
                    f"File: {fn.get('file', '')}\n"
                    f"{'Class' if is_class else 'Function'}: {fn.get('name', 'unknown')} (continued, part {part + 1})\n"
                    f"Source:\n{piece}"
                )
                metadatas.append(dict(metadatas[-1]))
                ids.append(f"doc_{doc_id}_part{part + 1}")
            doc_id += 1

    for file_no, file_info in enumerate(files):
        documents.append(f"File summary\n{file_outline(file_info)}")
        metadatas.append({"kind": "file", "file": file_info["path"], "function": ""})
        ids.append(f"file_{file_no}")

    return documents, metadatas, ids


def run_pipeline(
    repo_source: dict[str, Any],
    ai_engine: Any = None,
    collection_name: str | None = None,
) -> Iterator[dict[str, Any]]:
    local_path = repo_source.get("local_path")
    py_files = repo_source.get("py_files", [])

    if not local_path or not Path(local_path).exists():
        yield {"type": "error", "message": "Invalid or missing repository directory."}
        return

    if not py_files:
        yield {"type": "error", "message": "No valid Python (.py) source files found."}
        return

    # Sent before the vector store is touched: on a first run that step loads the
    # embedding model, and the screen would otherwise show nothing for several seconds.
    yield {"type": "progress", "function": "Index", "status": "preparing the vector index (slower on the first run)"}

    # A failed reset is not fatal: indexing below reports its own problems.
    with contextlib.suppress(Exception):
        reset_collection(collection_name)

    files = []
    all_functions_docs = []
    to_draft = []
    pending_cloud = []

    # --- 1. AST EXTRACTION ---
    for rel_file_path in py_files:
        normalized_path = rel_file_path.replace("\\", "/")

        yield {"type": "progress", "function": normalized_path, "status": "parsing"}

        try:
            code_content = read_source(Path(local_path, rel_file_path))
        except OSError as error:
            logger.warning("Skipped %s: %s", normalized_path, error)
            continue

        # The scan screen already parsed this file; reuse that (one dict copy per entry) instead of parsing again.
        parsed = (repo_source.get("definitions") or {}).get(normalized_path)
        funcs = [dict(d) for d in parsed] if parsed is not None else extract_definitions(code_content, file_path=normalized_path)
        files.append({
            "path": normalized_path,
            "module_doc": extract_module_docstring(code_content),
            "functions": funcs,
            "source": code_content,
            "bom": has_byte_order_mark(Path(local_path, rel_file_path)),
        })

        for fn in funcs:
            fn_name = fn.get("name", "unknown")
            # The model, the index and the screens always get LF; only the write-back uses the file as saved.
            fn_source = (fn.get("code") or fn.get("source") or "").replace("\r\n", "\n")
            fn["source"] = fn_source

            if fn.get("has_docstring", False):
                fn["is_ai_draft"] = False
                fn["doc_status"] = "original"
                fn["docstring"] = fn.get("docstring") or "(Original docstring retained)"
                yield {"type": "result", "function": fn_name, "docstring": "(Original docstring retained)", "file": normalized_path}
            elif fn.get("kind") == "class":
                fn["docstring"] = ""
                fn["is_ai_draft"] = False
                fn["doc_status"] = "not_drafted"
            else:
                # Never store an error message as documentation: a function stays
                # empty and "missing" until a model has actually drafted it.
                fn["docstring"] = ""
                fn["is_ai_draft"] = False
                fn["doc_status"] = "missing"
                to_draft.append(fn)

            all_functions_docs.append(fn)

    # --- 2. LOCAL AI ENGINE (batched; shortest first, so little padding is wasted) ---
    if len(to_draft) > MAX_LOCAL_DRAFTS:
        left = len(to_draft) - MAX_LOCAL_DRAFTS
        to_draft = to_draft[:MAX_LOCAL_DRAFTS]  # in source order, so the cap doesn't only drop long functions
        yield {
            "type": "progress",
            "function": "CodeT5",
            "status": f"{left} functions left without a docstring (limit {MAX_LOCAL_DRAFTS} per scan)",
        }
    to_draft.sort(key=lambda fn: len(fn["source"]))
    for start in range(0, len(to_draft), LOCAL_BATCH_SIZE):
        batch = to_draft[start:start + LOCAL_BATCH_SIZE]
        yield {
            "type": "progress",
            "function": "CodeT5",
            "status": f"drafting docstrings {start + 1}-{start + len(batch)} of {len(to_draft)}",
        }
        drafted = _local_docstrings(ai_engine, [fn["source"] for fn in batch])
        for fn, generated_doc in zip(batch, drafted, strict=True):
            if generated_doc:
                fn["docstring"] = generated_doc
                fn["is_ai_draft"] = True
                fn["doc_status"] = "local"
                yield {"type": "result", "function": fn.get("name", "unknown"), "docstring": generated_doc, "file": fn.get("file", "")}
            else:
                pending_cloud.append(fn)  # queue for the batched cloud fallback

    # --- 3. BATCHED CLOUD FALLBACK (bounded number of API calls) ---
    if pending_cloud:
        batches = [pending_cloud[i:i + CLOUD_BATCH_SIZE] for i in range(0, len(pending_cloud), CLOUD_BATCH_SIZE)]
        for batch_no, batch in enumerate(batches[:MAX_CLOUD_BATCHES], start=1):
            yield {
                "type": "progress",
                "function": "Cloud fallback",
                "status": f"drafting {len(batch)} docstrings (request {batch_no} of {min(len(batches), MAX_CLOUD_BATCHES)})",
            }
            try:
                docs = summarize_batch(batch)
            except Exception as error:  # noqa: BLE001 - provider errors come in many types
                logger.warning("Cloud docstring fallback failed: %s", error)
                yield {"type": "progress", "function": "Cloud fallback", "status": "cloud unreachable, stopping fallback"}
                break

            for idx, fn in enumerate(batch):
                doc = docs.get(idx)
                if doc:
                    fn["docstring"] = doc
                    fn["is_ai_draft"] = True
                    fn["doc_status"] = "cloud"
                    yield {"type": "result", "function": fn.get("name", "unknown"), "docstring": doc, "file": fn.get("file", "")}

        still_missing = sum(1 for fn in pending_cloud if fn["doc_status"] == "missing")
        if still_missing:
            yield {"type": "progress", "function": "Cloud fallback", "status": f"{still_missing} functions left without a docstring"}

    # --- 4. DOCUMENTED SOURCE + COVERAGE (all local) ---
    documented_files = {}
    patches = []
    for file_info in files:
        written = insert_docstrings(file_info["source"], file_info["functions"])
        if written["inserted"]:
            # A file that started with a byte-order mark keeps it, so the patch's first
            # line matches the file on disk and the documented copy is saved the same way.
            bom = "\ufeff" if file_info.get("bom") else ""
            documented_files[file_info["path"]] = bom + written["source"]
            patches.append(make_patch(file_info["path"], bom + file_info["source"], bom + written["source"]))
    coverage = build_coverage(files)

    # --- 5. VECTOR DATABASE INDEXING (functions, classes + per-file summaries) ---
    rag_documents, rag_metadatas, rag_ids = _build_index_entries(files)
    if rag_documents:
        try:
            add_documents(documents=rag_documents, metadatas=rag_metadatas, ids=rag_ids, collection_name=collection_name)
        except Exception as error:  # noqa: BLE001 - the docs are still usable without the index
            yield {"type": "progress", "function": "ChromaDB", "status": f"Vector indexing warning: {error}"}

    # --- 6. PARTIAL SAVE ---
    # Hand the local work to the caller before the cloud call, so a cloud failure cannot lose it.
    # The overview prompt is built from every file's functions and their docstrings.
    overview_context = repository_outline(files)
    final_data = {
        "type": "done",
        "overview": OVERVIEW_SKIPPED_MESSAGE,
        "overview_status": "skipped",
        "functions": all_functions_docs,
        "coverage": coverage,
        "documented_files": documented_files,
        "patch": "".join(patches),
    }
    save_results_cache(final_data)
    yield {"type": "partial", "data": final_data, "overview_context": overview_context}

    yield {"type": "progress", "function": "Repository", "status": "generating system overview via CrewAI"}

    # --- 7. CLOUD SYNTHESIS (GEMINI/CREWAI) ---
    try:
        final_data["overview"] = generate_overview(overview_context)
        final_data["overview_status"] = "ok"
        save_results_cache(final_data)
    except Exception as error:  # noqa: BLE001 - the local results were already handed over above
        logger.warning("Overview generation failed: %s", error)
        yield {"type": "rate_limited", "message": str(error)}
        return

    try:
        index_overview(final_data["overview"], collection_name)
    except Exception as error:  # noqa: BLE001 - the overview is still shown without the index
        yield {"type": "progress", "function": "ChromaDB", "status": f"Vector indexing warning: {error}"}

    yield final_data
