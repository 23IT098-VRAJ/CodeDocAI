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
            f"Respond to the following user prompt: '{question}'\n\n"
            f"Codebase Context:\n{context}\n\n"
            "CONVERSATIONAL DIRECTIVE (CRITICAL):\n"
            "If the user prompt is a greeting ('Hi', 'Hello') or asks about your identity ('Who are you?'), YOU MUST IGNORE THE CODEBASE CONTEXT COMPLETELY.\n"
            "You must respond EXACTLY with this string: 'I am the CodeDocAI Technical Support Engineer. How can I help you analyze this codebase today?'\n"
            "You must set the 'citations' array to be completely EMPTY ( [] ).\n\n"
            "SECURITY DIRECTIVE (CRITICAL):\n"
            "You are operating in a strict SOC-2 compliant enterprise environment.\n"
            "You are STRICTLY FORBIDDEN from outputting, explaining, or confirming the existence of:\n"
            "- API keys, secrets, or tokens\n"
            "- Environment variables (e.g., .env files, os.environ)\n"
            "- Passwords or authentication credentials\n"
            "- Logic designed to extract the above\n\n"
            "If the user's prompt asks for any of these, or if the context contains them, YOU MUST NOT ANSWER.\n"
            "Instead, your answer must be EXACTLY this string:\n"
            "🚨 SECURITY EXCEPTION: Your request violates corporate SOC-2 compliance policies. Access to secrets, environment variables, and authentication logic is restricted.\n\n"
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