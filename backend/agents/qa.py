"""
backend/agents/qa.py
CrewAI agent responsible for answering user questions using retrieved ChromaDB context.
Enforces the A.4 data contract for structured citations.
"""

import json
from crewai import Agent, Task, Crew, Process
from backend.resilience.rate_limiter import execute_with_failover

def _qa_logic(llm, question: str, context: str) -> dict:
    qa_agent = Agent(
        role='Codebase Technical Support Engineer',
        goal='Answer developer questions accurately based ONLY on the provided RAG context.',
        backstory='An expert software architect who answers questions by citing specific functions and files.',
        verbose=False,
        allow_delegation=False,
        llm=llm
    )

    qa_task = Task(
        description=(
            f"Answer the following technical question about the codebase: '{question}'\n\n"
            f"Use ONLY the following context to formulate your answer:\n{context}\n\n"
            "You MUST output exactly valid JSON matching this schema:\n"
            "{\n"
            '  "answer": "Your detailed, markdown-formatted answer here.",\n'
            '  "citations": [{"function": "function_name", "file": "file_path.py"}]\n'
            "}\n"
            "Output ONLY the raw JSON string. Do NOT wrap it in ```json blocks. Do NOT include any conversational text."
        ),
        expected_output="A raw JSON object containing 'answer' and 'citations'.",
        agent=qa_agent
    )

    crew = Crew(agents=[qa_agent], tasks=[qa_task], process=Process.sequential)
    
    # 1. Execute the call. DO NOT catch API exceptions here! Let them bubble up to the Load Balancer.
    result = crew.kickoff()
    
    # 2. If it succeeds, safely parse the JSON
    clean_result = result.raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(clean_result)
    except json.JSONDecodeError as e:
        print(f"\n[!] QA Agent JSON Formatting Error: {e}\n")
        return {
            "answer": clean_result,  # Return the raw text if JSON parsing fails
            "citations": []
        }

def answer_codebase_question(question: str, context: str) -> dict:
    """Uses the custom load balancer to answer codebase questions."""
    return execute_with_failover(lambda llm: _qa_logic(llm, question, context))