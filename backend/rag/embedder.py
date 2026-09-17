from sentence_transformers import SentenceTransformer, util

# Loaded once at module import to prevent reloading on every function call.
# all-MiniLM-L6-v2 is highly optimized and requires minimal RAM.
MODEL_NAME = 'all-MiniLM-L6-v2'
embedder_model = SentenceTransformer(MODEL_NAME)

def format_chunk(name: str, docstring: str, code: str) -> str:
    """
    Formats the parsed function data into a single semantically rich string 
    to provide clear boundaries for the embedding model.
    """
    return f"Function: {name}\nDocstring: {docstring}\nCode:\n{code}"

def get_embedding(text: str) -> list[float]:
    """
    Generates a dense vector embedding for the input text.
    Returns a Python list of floats (required format for ChromaDB ingestion).
    """
    # Generate the embedding as a flat numpy array, then convert to a standard list
    embedding = embedder_model.encode(text, convert_to_numpy=True)
    return embedding.tolist()

# --- Built-in Test Block ---
if __name__ == "__main__":
    print("=== Testing Embedder ===")
    
    # 1. Test formatting
    test_name = "add_numbers"
    test_doc = "Adds two integers together."
    test_code = "def add_numbers(a, b):\n    return a + b"
    
    formatted_text = format_chunk(test_name, test_doc, test_code)
    print("--- Formatted Chunk ---")
    print(formatted_text)
    
    # 2. Test embedding generation and semantic similarity
    print("\n--- Generating Embeddings ---")
    vec1 = get_embedding(formatted_text)
    print(f"Embedding generated. Vector dimension: {len(vec1)}")
    
    # Create a semantically similar chunk (math) and a dissimilar chunk (database)
    math_chunk = format_chunk("subtract", "Subtracts b from a", "def subtract(a, b):\n    return a - b")
    db_chunk = format_chunk("connect_db", "Connects to postgres", "def connect_db(uri):\n    pass")
    
    vec2_math = get_embedding(math_chunk)
    vec3_db = get_embedding(db_chunk)
    
    # Calculate cosine similarity
    sim_math = util.cos_sim(vec1, vec2_math).item()
    sim_db = util.cos_sim(vec1, vec3_db).item()
    
    print("\n--- Semantic Similarity Test ---")
    print(f"Similarity (Add vs Subtract): {sim_math:.4f}  <-- Should be higher")
    print(f"Similarity (Add vs Connect DB): {sim_db:.4f}  <-- Should be lower")