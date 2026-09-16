"""
fixtures.py -- CodeDocAI
Mock data fixtures and Q&A answer helper.
"""


# ---------------------------------------------------------------------------
# MOCK DATA FIXTURES  (Session 2)
# ---------------------------------------------------------------------------
_FIXTURE_DEFAULT = [
    {"path": "app.py",                    "functions": 8, "missing": 3},
    {"path": "auth/utils.py",             "functions": 4, "missing": 2},
    {"path": "models/task.py",            "functions": 6, "missing": 0},
    {"path": "services/email_sender.py",  "functions": 3, "missing": 3},
    {"path": "tests/test_auth.py",        "functions": 5, "missing": 0},
]
_FIXTURE_CLEAN = [
    {"path": "app.py",                    "functions": 8, "missing": 0},
    {"path": "auth/utils.py",             "functions": 4, "missing": 0},
    {"path": "models/task.py",            "functions": 6, "missing": 0},
    {"path": "services/email_sender.py",  "functions": 3, "missing": 0},
    {"path": "tests/test_auth.py",        "functions": 5, "missing": 0},
]

# ---------------------------------------------------------------------------
# MOCK DATA FIXTURES  (Session 4) -- per-function detail for files with missing > 0
# Keys match paths in _FIXTURE_DEFAULT that have missing > 0.
# Files with missing == 0 are rendered via the clean-file template instead.
# If a file with missing > 0 has no entry here, a fallback message is shown.
# ---------------------------------------------------------------------------
_FIXTURE_FUNCTIONS = {
    "app.py": {
        "module_summary": "This file defines the core task operations for the application.",
        "functions": [
            {
                "name": "create_task(title, due_date, assignee)",
                "docstring": "Creates a new task with the given title, due date, and assignee, appends it to the task list, and returns it.",
                "source": "def create_task(title, due_date, assignee):\n    task = {\n        \"title\": title,\n        \"due\": due_date,\n        \"owner\": assignee,\n        \"done\": False,\n    }\n    task_list.append(task)\n    return task",
            },
            {
                "name": "delete_task(task_id)",
                "docstring": "Removes the task with the given ID from the task list.",
                "source": "def delete_task(task_id):\n    global task_list\n    task_list = [t for t in task_list if t[\"id\"] != task_id]",
            },
            {
                "name": "assign_owner(task_id, new_owner)",
                "docstring": "Reassigns the task with the given ID to a new owner and returns the updated task.",
                "source": "def assign_owner(task_id, new_owner):\n    for t in task_list:\n        if t[\"id\"] == task_id:\n            t[\"owner\"] = new_owner\n            return t",
            },
        ],
    },
    "auth/utils.py": {
        "module_summary": "This module handles password hashing and session token verification for the authentication flow.",
        "functions": [
            {
                "name": "hash_password(password)",
                "docstring": "Hashes a plaintext password using SHA-256 and returns the hex digest for storage.",
                "source": "def hash_password(password):\n    return hashlib.sha256(\n        password.encode()\n    ).hexdigest()",
            },
            {
                "name": "verify_token(token, secret)",
                "docstring": "Verifies a session token against the given secret and returns whether it is valid.",
                "source": "def verify_token(token, secret):\n    expected = hmac.new(\n        secret.encode(),\n        token.encode(),\n        \"sha256\"\n    )\n    return hmac.compare_digest(\n        expected.hexdigest(),\n        token\n    )",
            },
        ],
    },
    "services/email_sender.py": {
        "module_summary": "This module handles outbound reminder and digest emails for upcoming tasks.",
        "functions": [
            {
                "name": "send_reminder(task, recipient)",
                "docstring": "Sends a reminder email for an upcoming task to the given recipient.",
                "source": "def send_reminder(task, recipient):\n    subject = format_subject_line(task)\n    smtp_client.send(recipient, subject, task[\"title\"])",
            },
            {
                "name": "format_subject_line(task)",
                "docstring": "Builds the email subject line from the task's title and due date.",
                "source": "def format_subject_line(task):\n    return f\"Reminder: {task['title']} due {task['due']}\"",
            },
            {
                "name": "queue_digest(tasks, recipient)",
                "docstring": "Queues a daily digest email summarizing the given tasks for the recipient.",
                "source": "def queue_digest(tasks, recipient):\n    digest_queue.append({\n        \"tasks\": tasks,\n        \"to\": recipient,\n    })",
            },
        ],
    },
}

# ---------------------------------------------------------------------------
# MOCK DATA FIXTURES  (Session 5) -- Q&A ground-truth knowledge base
# ---------------------------------------------------------------------------
_FIXTURE_QA = [
    {
        "keywords": ["create a task", "create task", "new task", "add a task", "add task"],
        "path": "app.py",
        "function": "create_task()",
        "answer": "Call create_task with a title, due date, and assignee. It builds a task dict, appends it to the task list, and returns the new task.",
    },
    {
        "keywords": ["delete a task", "delete task", "remove a task", "remove task"],
        "path": "app.py",
        "function": "delete_task()",
        "answer": "Call delete_task with a task's ID. It filters that task out of the task list.",
    },
    {
        "keywords": ["assign", "reassign", "change owner", "task owner"],
        "path": "app.py",
        "function": "assign_owner()",
        "answer": "Call assign_owner with a task ID and a new owner. It finds the matching task, updates its owner, and returns the updated task.",
    },
    {
        "keywords": ["hash", "password"],
        "path": "auth/utils.py",
        "function": "hash_password()",
        "answer": "Passwords are hashed with SHA-256 through hash_password, which returns the hex digest for storage.",
    },
    {
        "keywords": ["token", "session", "verify"],
        "path": "auth/utils.py",
        "function": "verify_token()",
        "answer": "verify_token checks a session token against a secret using HMAC and returns whether it's valid.",
    },
    {
        "keywords": ["reminder", "reminder email", "send an email", "send email"],
        "path": "services/email_sender.py",
        "function": "send_reminder()",
        "answer": "send_reminder builds a subject line for a task and sends a reminder email to the given recipient.",
    },
    {
        "keywords": ["subject line", "subject"],
        "path": "services/email_sender.py",
        "function": "format_subject_line()",
        "answer": "format_subject_line builds an email subject line from a task's title and due date.",
    },
    {
        "keywords": ["digest", "daily summary", "daily digest"],
        "path": "services/email_sender.py",
        "function": "queue_digest()",
        "answer": "queue_digest adds a task list and recipient to the digest queue, to be sent later as a daily summary.",
    },
]


def _answer_question(question: str) -> dict:
    """
    Match question against _FIXTURE_QA keyword entries (case-insensitive substring match).
    First entry with any keyword match wins.
    Returns: {"content": str, "citation": str | None}
    """
    q_lower = question.lower()
    for entry in _FIXTURE_QA:
        for kw in entry["keywords"]:
            if kw.lower() in q_lower:
                return {
                    "content": entry["answer"],
                    "citation": f"{entry['path']} \u00B7 {entry['function']}",
                }
    return {
        "content": (
            "Nothing in this codebase answers that \u2014 try asking about "
            "task creation, authentication, or email reminders."
        ),
        "citation": None,
    }
