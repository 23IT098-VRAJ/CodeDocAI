from crewai import Agent, Task, Crew, Process
from backend.resilience.rate_limiter import execute_with_failover

def _generate_docstring_logic(llm, func_name: str, func_source: str, file_path: str) -> str:
    writer_agent = Agent(
        role="Senior Python Documentation Engineer",
        goal="Write concise, standard Python docstrings for undocumented functions.",
        backstory=(
            "You are a PEP 257 standards specialist. You read function signatures, "
            "arguments, and execution bodies to extract intent, parameters, and return types. "
            "You write idiomatic Google-style docstrings without preamble."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False
    )

    doc_task = Task(
        description=(
            f"Analyze the function `{func_name}` located in `{file_path}`.\n\n"
            f"FUNCTION SOURCE:\n```python\n{func_source}\n```\n\n"
            "Generate a concise Google-style docstring for this function. "
            "Explain the purpose, list `Args` with types if identifiable, and define `Returns`. "
            "Output ONLY the raw docstring text enclosed in triple double quotes (\"\"\")."
        ),
        expected_output=(
            "A standard Google-style triple-quoted docstring. Do not include markdown code block "
            "delimiters (no ```python or ```), greetings, or explanations outside the quotes."
        ),
        agent=writer_agent
    )

    crew = Crew(agents=[writer_agent], tasks=[doc_task], process=Process.sequential)
    result = crew.kickoff()
    raw_doc = str(result).strip()
    
    if raw_doc.startswith("```") and raw_doc.endswith("```"):
        lines = raw_doc.split("\n")
        raw_doc = "\n".join(lines[1:-1]).strip()
        
    return raw_doc

def generate_function_docstring(func_name: str, func_source: str, file_path: str = "") -> str:
    """Uses the custom load balancer to generate the docstring."""
    return execute_with_failover(lambda llm: _generate_docstring_logic(llm, func_name, func_source, file_path))