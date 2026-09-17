"""
backend/rag/vectorstore.py
ChromaDB vector store integration for indexing and retrieving codebase context.
"""
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# Use an in-memory client for session-isolated security
chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))
COLLECTION_NAME = "codedocai_codebase"

# Bypass Google's API and Chroma's buggy ONNX downloader.
# This uses the PyTorch/SentenceTransformers library already installed in your environment,
# pulling securely and quickly from Hugging Face's stable CDN.
hf_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

def get_collection():
    return chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=hf_ef
    )

def reset_collection():
    """Deletes the existing collection to ensure a clean slate for new scans."""
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
    except ValueError:
        pass

def add_documents(documents: list, metadatas: list, ids: list):
    """Adds code snippets and docstrings to the vector store."""
    if not documents:
        return
    collection = get_collection()
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

def query_similar(query: str, n_results: int = 3) -> list:
    """Queries the vector store for context similar to the user's question."""
    collection = get_collection()
    if collection.count() == 0:
        return []
        
    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count())
    )
    
    if results and results.get("documents") and results["documents"][0]:
        return results["documents"][0]
    return []