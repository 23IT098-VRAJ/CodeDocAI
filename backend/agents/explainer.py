from crewai import Agent, Task, Crew, Process
from backend.resilience.rate_limiter import execute_with_failover

def _generate_logic(llm, file_path: str, code_content: str) -> str:
    explainer_agent = Agent(
        role="Senior Technical Writer",
        goal="Analyze Python source code and extract its primary structural purpose.",
        backstory=(
            "You are an expert documentation engineer. You read raw source code "
            "and instantly understand its architectural intent. You write clean, "
            "precise, and highly structured technical overviews."
        ),
        llm=llm, 
        verbose=False,
        allow_delegation=False
    )

    analysis_task = Task(
        description=(
            f"Analyze the following Python code from the file `{file_path}`.\n\n"
            f"CODE:\n```python\n{code_content}\n```\n\n"
            "Write a concise, 2-to-3 sentence overview explaining what this specific "
            "module does. Focus strictly on its functional purpose within a larger system."
        ),
        expected_output=(
            "A strict Markdown string starting with a `## {Filename} Overview` header, "
            "followed by a 2-to-3 sentence functional description. Do not include introductory "
            "greetings or conversational filler."
        ),
        agent=explainer_agent
    )

    crew = Crew(agents=[explainer_agent], tasks=[analysis_task], process=Process.sequential)
    result = crew.kickoff()
    return str(result)

def generate_module_overview(file_path: str, code_content: str) -> str:
    """Uses the custom load balancer to generate the overview."""
    return execute_with_failover(lambda llm: _generate_logic(llm, file_path, code_content))