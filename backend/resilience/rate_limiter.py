"""
backend/resilience/rate_limiter.py
Enterprise-grade load balancer and failover router for CrewAI agents.
Implements Phase 5 architecture rules.
"""
import os
import json
import time
from typing import Callable, Any
from crewai import LLM

_COOLDOWN_FILE = "api_cooldowns.json"
_COOLDOWN_SECONDS = 120  # 2-minute cooling period

def get_keys():
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_1 = os.environ.get("GEMINI_API_KEY_1")
    gemini_2 = os.environ.get("GEMINI_API_KEY_2")
    groq_1 = os.environ.get("GROQ_API_KEY_1")
    groq_2 = os.environ.get("GROQ_API_KEY_2")
    
    try:
        import streamlit as st
        gemini_1 = st.secrets.get("GEMINI_API_KEY_1", gemini_1)
        gemini_2 = st.secrets.get("GEMINI_API_KEY_2", gemini_2)
        groq_1 = st.secrets.get("GROQ_API_KEY_1", groq_1)
        groq_2 = st.secrets.get("GROQ_API_KEY_2", groq_2)
    except Exception:
        pass
        
    return {
        "GEMINI_1": gemini_1,
        "GEMINI_2": gemini_2,
        "GROQ_1": groq_1,
        "GROQ_2": groq_2,
    }

def _load_state():
    if os.path.exists(_COOLDOWN_FILE):
        try:
            with open(_COOLDOWN_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _mark_cooling(provider_id: str):
    state = _load_state()
    state[provider_id] = time.time() + _COOLDOWN_SECONDS
    try:
        with open(_COOLDOWN_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        pass

def _get_active_llm():
    state = _load_state()
    now = time.time()
    keys = get_keys()
    
    # Priority Hierarchy: Gemini First, Groq as Fallback
    hierarchy = [
        ("GEMINI_1", "gemini/gemini-3.6-flash", keys.get("GEMINI_1")),
        ("GEMINI_2", "gemini/gemini-3.6-flash", keys.get("GEMINI_2")),
        ("GROQ_1", "groq/llama-3.1-8b-instant", keys.get("GROQ_1")),
        ("GROQ_2", "groq/llama-3.1-8b-instant", keys.get("GROQ_2")),
    ]
    
    for pid, model_str, key_val in hierarchy:
        if not key_val or not key_val.strip():
            continue
            
        cooldown_expiry = state.get(pid, 0)
        if now > cooldown_expiry:
            if "gemini" in model_str:
                os.environ["GEMINI_API_KEY"] = key_val
            elif "groq" in model_str:
                os.environ["GROQ_API_KEY"] = key_val
                
            return LLM(model=model_str, api_key=key_val), pid

    raise Exception("ALL_APIS_COOLING")

def execute_with_failover(agent_builder_func: Callable[[LLM], Any]) -> Any:
    """
    Executes a CrewAI kickoff. If rate-limited or experiencing transient node drops,
    marks the key for a 2-minute cooldown and instantly retries with the next available key.
    """
    max_retries = 4
    
    for attempt in range(max_retries):
        try:
            active_llm, active_pid = _get_active_llm()
            print(f"⚡ Load Balancer routing task to: {active_pid}")
            return agent_builder_func(active_llm)
            
        except Exception as e:
            err_str = str(e).lower()
            
            if "all_apis_cooling" in err_str:
                raise Exception("All API keys are currently in a 2-minute cooldown. Please wait.")
            
            # Enhanced Catcher: Now includes Groq's weird 404 and model_not_found drops
            transient_errors = ["429", "quota", "rate", "503", "unavailable", "404", "model_not_found", "not found"]
            
            if any(err in err_str for err in transient_errors):
                print(f"[!] {active_pid} overloaded or dropped connection. Entering 120s cooldown...")
                _mark_cooling(active_pid)
                continue 
                
            raise e
            
    raise Exception("All failover attempts exhausted.")