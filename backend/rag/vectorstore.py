"""
backend/rag/vectorstore.py
ChromaDB vector store integration for indexing and retrieving codebase context.

The client lives in memory and is shared by the whole process, so every browser
session works in its own collection (pass collection_name) to keep one user's
code out of another user's answers.
"""
import contextlib
import threading
from typing import Any

DEFAULT_COLLECTION = "codedocai_codebase"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

_lock = threading.Lock()
_client = None
_embedding_fn = None


def _get_client() -> Any:
    """Creates the in-memory client and the embedding model on first use."""
    global _client, _embedding_fn
    with _lock:
        if _client is None:
            import chromadb
            from chromadb.config import Settings
            from chromadb.utils import embedding_functions

            # Uses the local SentenceTransformers model instead of Chroma's ONNX downloader.
            try:
                # Normal case: the model is already in the Hugging Face cache on this
                # machine. Loading it from there makes no network request at all, so the
                # app starts without internet and does not announce itself to the Hub.
                _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=EMBEDDING_MODEL, local_files_only=True
                )
            except Exception:  # noqa: BLE001 - the library raises several types when the cache is empty
                # First run on this machine: download the model once.
                _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=EMBEDDING_MODEL
                )
            _client = chromadb.Client(Settings(anonymized_telemetry=False))
    return _client


def get_collection(collection_name: str | None = None) -> Any:
    client = _get_client()
    return client.get_or_create_collection(
        name=collection_name or DEFAULT_COLLECTION,
        embedding_function=_embedding_fn,
    )


def reset_collection(collection_name: str | None = None) -> None:
    """Deletes the collection to ensure a clean slate for new scans."""
    with contextlib.suppress(Exception):  # nothing to delete
        _get_client().delete_collection(name=collection_name or DEFAULT_COLLECTION)


def add_documents(
    documents: list[str], metadatas: list[dict], ids: list[str], collection_name: str | None = None
) -> None:
    """Adds entries to the vector store. An entry whose id already exists is replaced."""
    if not documents:
        return
    get_collection(collection_name).upsert(documents=documents, metadatas=metadatas, ids=ids)


def query_chunks(query: str, n_results: int = 4, collection_name: str | None = None) -> list[dict]:
    """
    Returns the entries most similar to the question, best match first, as
    {"document": str, "metadata": {"kind", "file", "function"}}.
    """
    collection = get_collection(collection_name)
    count = collection.count()
    if count == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, count),
        include=["documents", "metadatas"],
    )
    documents = (results.get("documents") or [[]])[0] or []
    metadatas = (results.get("metadatas") or [[]])[0] or []

    chunks = []
    for i, document in enumerate(documents):
        metadata = metadatas[i] if i < len(metadatas) and metadatas[i] else {}
        chunks.append({"document": document, "metadata": dict(metadata)})
    return chunks


def query_similar(query: str, n_results: int = 3, collection_name: str | None = None) -> list[str]:
    """Text-only variant of query_chunks."""
    return [chunk["document"] for chunk in query_chunks(query, n_results, collection_name)]
