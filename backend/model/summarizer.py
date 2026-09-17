"""
backend/model/summarizer.py
Connects function documentation extraction to the live Docstring Writer agent.
"""

from backend.agents.docwriter import generate_function_docstring


def summarize_code(code: str, func_name: str = "function", file_path: str = "") -> str:
    """
    Generates a Google-style docstring for an undocumented function using the Docstring Writer agent.
    """
    if not code or not code.strip():
        return '"""No source code provided."""'

    try:
        docstring = generate_function_docstring(
            func_name=func_name,
            func_source=code,
            file_path=file_path
        )
        return docstring
    except Exception as e:
        return f'"""Error generating docstring: {str(e)}"""'