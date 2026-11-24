from backend.resilience.rate_limiter import execute_with_failover
from backend.security import redact


def _generate_logic(llm, outline: str) -> str:
    from crewai import Agent, Crew, Process, Task

    explainer_agent = Agent(
        role="Senior Technical Writer",
        goal="Explain the architecture of a Python repository from an outline of its files and functions.",
        backstory=(
            "You are an expert documentation engineer. You read the structure of a codebase "
            "and understand its architectural intent. You write clean, "
            "precise, and highly structured technical overviews."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False
    )

    analysis_task = Task(
        description=(
            "Below is an outline of a Python repository. Each FILE entry lists its purpose "
            "(when known) and its classes and functions with a one-line summary.\n\n"
            f"OUTLINE:\n{outline}\n\n"
            "Write an architecture overview of this repository. Base it ONLY on the outline; "
            "do not invent files, functions, or behaviour that are not listed."
        ),
        expected_output=(
            "A strict Markdown string with exactly these parts:\n"
            "1. A `## Repository Architecture Overview` header followed by 2-to-3 sentences on what the system does.\n"
            "2. A `### Modules` header followed by a bullet list, one line per file (at most 10 of the most "
            "important files), written as `- `path`: its role`.\n"
            "3. A `### How It Fits Together` header followed by 2-to-3 sentences on how the modules interact.\n"
            "Do not include introductory greetings or conversational filler."
        ),
        agent=explainer_agent
    )

    crew = Crew(agents=[explainer_agent], tasks=[analysis_task], process=Process.sequential)
    result = crew.kickoff()
    return str(result)


def _offline_overview() -> str:
    return (
        "## Repository Architecture Overview\n\n"
        "[OFFLINE TEST] Placeholder overview. No cloud API call was made."
    )


def generate_repository_overview(outline: str) -> str:
    """One cloud request that turns the repository outline into an architecture overview."""
    outline = redact(outline)  # default argument values in signatures can hold credentials
    return execute_with_failover(
        lambda llm: _generate_logic(llm, outline),
        offline_result=_offline_overview,
    )
