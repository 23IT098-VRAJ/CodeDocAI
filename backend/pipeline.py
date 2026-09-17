"""
backend/pipeline.py
Core pipeline orchestrator integrating AST extraction, local CodeT5 Engine, 
CrewAI agents, and ChromaDB indexing.
"""

import os
import json
import torch
from pathlib import Path
import streamlit as st
from typing import Generator, Dict, Any

from backend.parser.extractor import extract_functions
from backend.model.summarizer import summarize_code
from backend.agents.explainer import generate_module_overview
from backend.rag.vectorstore import add_documents, reset_collection

# Lock the cache path strictly to the project root
_ROOT_DIR = Path(__file__).resolve().parents[1]
_CACHE_PATH = _ROOT_DIR / "docs_cache.json"

# Update signature to accept the cached ai_engine from generation.py
def run_pipeline(repo_source: Dict[str, Any], ai_engine: Any = None) -> Generator[Dict[str, Any], None, None]:
    local_path = repo_source.get("local_path")
    py_files = repo_source.get("py_files", [])

    if not local_path or not os.path.exists(local_path):
        yield {"type": "error", "message": "Invalid or missing repository directory."}
        return

    if not py_files:
        yield {"type": "error", "message": "No valid Python (.py) source files found."}
        return

    try:
        reset_collection()
    except Exception:
        pass

    all_functions_docs = []
    rag_documents = []
    rag_metadatas = []
    rag_ids = []
    doc_id_counter = 0

    combined_overview_context = []

    for rel_file_path in py_files:
        abs_file_path = os.path.join(local_path, rel_file_path)
        normalized_path = rel_file_path.replace("\\", "/")

        yield {"type": "progress", "function": normalized_path, "status": "parsing"}

        try:
            with open(abs_file_path, "r", encoding="utf-8", errors="ignore") as f:
                code_content = f.read()
        except Exception:
            continue

        funcs = extract_functions(code_content, file_path=normalized_path)
        
        combined_overview_context.append(f"FILE: {normalized_path}\n{code_content[:800]}\n")

        for fn in funcs:
            fn_name = fn.get("name", "unknown")
            
            fn_source = fn.get("code") or fn.get("source") or ""
            fn["source"] = fn_source  
            
            has_docstring = fn.get("has_docstring", False)

            if not has_docstring:
                yield {"type": "progress", "function": f"{normalized_path}::{fn_name}", "status": "summarizing via CodeT5"}
                
                generated_doc = None
                
                # --- 1. LOCAL AI ENGINE EXECUTION ---
                # Fallback to st.session_state if not explicitly passed
                engine = ai_engine or st.session_state.get("ai_engine")
                
                if engine and fn_source.strip():
                    try:
                        tokenizer, model, device = engine
                        
                        # Apply identical inference constraints as the benchmark
                        inputs = tokenizer(fn_source, max_length=384, truncation=True, return_tensors="pt").to(device)
                        with torch.no_grad():
                            outputs = model.generate(
                                input_ids=inputs["input_ids"],
                                attention_mask=inputs["attention_mask"],
                                max_length=64,
                                num_beams=4,
                                no_repeat_ngram_size=3,
                                early_stopping=True
                            )
                        
                        generated_doc = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
                    except Exception as e:
                        print(f"[!] Local CodeT5 Generation Failed: {e}")
                
                # --- 2. FALLBACK API EXECUTION ---
                # If local generation fails or is missing, drop down to the original summarizer module
                if not generated_doc:
                    generated_doc = summarize_code(
                        code=fn_source,
                        func_name=fn_name,
                        file_path=normalized_path
                    )
                
                fn["docstring"] = generated_doc
                fn["is_ai_draft"] = True
                yield {"type": "result", "function": fn_name, "docstring": generated_doc, "file": normalized_path}
            else:
                fn["is_ai_draft"] = False
                fn["docstring"] = fn.get("docstring") or "(Original docstring retained)"
                yield {"type": "result", "function": fn_name, "docstring": "(Original docstring retained)", "file": normalized_path}

            all_functions_docs.append(fn)

            rag_text = (
                f"File: {normalized_path}\n"
                f"Function: {fn_name}\n"
                f"Docstring: {fn['docstring']}\n"
                f"Source:\n{fn_source}"
            )
            rag_documents.append(rag_text)
            rag_metadatas.append({"file": normalized_path, "function": fn_name})
            rag_ids.append(f"doc_{doc_id_counter}")
            doc_id_counter += 1

    # --- 3. VECTOR DATABASE INDEXING ---
    if rag_documents:
        try:
            add_documents(documents=rag_documents, metadatas=rag_metadatas, ids=rag_ids)
        except Exception as e:
            yield {"type": "progress", "function": "ChromaDB", "status": f"Vector indexing warning: {str(e)}"}

    yield {"type": "progress", "function": "Repository", "status": "generating system overview via CrewAI"}
    
    # --- 4. CLOUD SYNTHESIS (GEMINI/CREWAI) ---
    overview_text = ""
    try:
        sample_code_block = "\n---\n".join(combined_overview_context[:8])
        overview_text = generate_module_overview("Repository Architecture", sample_code_block)
    except Exception as e:
        print(f"\n[!] CrewAI Generation Failed: {str(e)}\n")
        yield {"type": "rate_limited", "message": str(e)}
        return

    final_data = {
        "type": "done",
        "overview": overview_text,
        "functions": all_functions_docs
    }
    
    st.session_state["pipeline_results"] = final_data
    
    try:
        with open(_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(final_data, f)
    except Exception as e:
        print(f"Cache write failed: {e}")
        pass
        
    yield final_data