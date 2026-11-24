"""
backend/security.py
Local security checks. Nothing here calls the cloud.

classify_question   rates a Q&A question; CRITICAL ones are refused before any API
                    call is made, and the same rating is used for the audit log.
redact_secrets      removes credentials from text before it is sent to a cloud model.
"""
import logging
import re

logger = logging.getLogger(__name__)

SECURITY_PREFIX = "Request blocked."
SECURITY_REFUSAL = (
    "Request blocked. Q&A won’t give out secrets, credentials or environment values from this "
    "codebase, and it ignores instructions to change how it works."
)
REDACTED = "[REDACTED]"

# ---------------------------------------------------------------------------
# Question classification
# ---------------------------------------------------------------------------

# Verbs that ask for something to be handed over.
_HAND_OVER = r"\b(?:give|provide|send|share|reveal|leak|dump|expose|steal|hand|want|need)\b"
# "key" used as an adjective ("the key functions") is not a request for a credential.
_KEY_AS_ADJECTIVE = (
    r"(?!\s+(?:functions?|features?|points?|components?|ideas?|concepts?|parts?|steps?|differences?"
    r"|class(?:es)?|modules?|files?|takeaways?|aspects?|elements?|roles?|purpose|responsibilit(?:y|ies)"
    r"|methods?|logic|areas?|things?|details?|design|decisions?))"
)

_CRITICAL_PATTERNS = [
    # credentials
    r"\bapi ?keys?\b",
    r"\b(?:secret|private|access|ssh|encryption|signing) keys?\b",
    rf"{_HAND_OVER}[^.?!]*\bkeys?\b{_KEY_AS_ADJECTIVE}",
    r"\bsecrets?\b",
    r"\bpasswords?\b",
    r"\bpasswd\b",
    r"\bcredentials?\b",
    r"\b(?:auth|access|bearer|api|session|jwt|refresh|sso|oauth) tokens?\b",
    rf"{_HAND_OVER}[^.?!]*\btokens?\b",
    # environment
    r"\benv(?:ironment)? ?(?:vars?|variables?)\b",
    r"\.env\b",
    r"\bos\.environ\b",
    r"\bdotenv\b",
    # prompt injection
    r"\b(?:ignore|disregard|forget) (?:all )?(?:of )?(?:the |your )?(?:previous|prior|above|earlier) (?:instructions?|prompts?|rules?)\b",
    r"\bsystem prompt\b",
    r"\byou are now\b",
    r"\b(?:configuration|config) (?:strings?|values?)\b",
    r"\bjailbreak\b",
    r"\bdeveloper mode\b",
]
_WARNING_PATTERNS = [
    r"\bdatabase\b",
    r"\bauth(?:entication|orization|enticate|orize)?\b",
    r"\bbypass(?:ed|es|ing)?\b",
]
_CRITICAL_RE = re.compile("|".join(_CRITICAL_PATTERNS))
_WARNING_RE = re.compile("|".join(_WARNING_PATTERNS))


def _normalize(question: str) -> str:
    """Lower case, with _ and - read as spaces, so GEMINI_API_KEY_1 reads as 'gemini api key 1'."""
    text = re.sub(r"[_\-]+", " ", (question or "").lower())
    return re.sub(r"\s+", " ", text).strip()


def classify_question(question: str) -> str:
    """
    "CRITICAL"  asks for credentials or environment values, or tries to override the
                assistant’s instructions. These are refused locally.
    "WARNING"   touches authentication or database topics. Answered, but flagged.
    "INFO"      everything else.

    Whole words are matched, so "tokenizer", "keyword" and "author" are not flagged.
    """
    text = _normalize(question)
    if _CRITICAL_RE.search(text):
        return "CRITICAL"
    if _WARNING_RE.search(text):
        return "WARNING"
    return "INFO"


def is_blocked(question: str) -> bool:
    return classify_question(question) == "CRITICAL"


# ---------------------------------------------------------------------------
# Secret redaction
# ---------------------------------------------------------------------------

_PRIVATE_KEY_RE = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL
)

# Recognisable credential formats, wherever they appear.
_TOKEN_RE = re.compile("|".join([
    r"AIza[0-9A-Za-z_\-]{35}",                                      # Google API key
    r"gsk_[A-Za-z0-9]{20,}",                                        # Groq
    r"sk-[A-Za-z0-9_\-]{20,}",                                      # OpenAI / Anthropic style
    r"gh[pousr]_[A-Za-z0-9]{36,}",                                  # GitHub token
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"AKIA[0-9A-Z]{16}",                                            # AWS access key id
    r"xox[baprs]-[A-Za-z0-9\-]{10,}",                               # Slack
    r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}",  # JWT
]))

# user:password@ inside a URL
_URL_CREDENTIALS_RE = re.compile(r"(?<=://)[^/\s:@'\"]+:[^/\s:@'\"]+(?=@)")

# A string literal assigned to a name that says it is a credential:
#   password = "x"    API_KEY: str = 'x'    {"token": "x"}
_SECRET_NAME = (
    r"[A-Za-z0-9_]*(?:password|passwd|pwd|secret|token|api_?key|apikey|access_?key|private_?key|auth_?key|credential)"
    r"[A-Za-z0-9_]*"
)
_ASSIGNMENT_RE = re.compile(
    rf"(?P<head>[\"']?\b{_SECRET_NAME}[\"']?\s*(?::\s*[\w\[\]., |]+?\s*=|[:=])\s*[rbfuRBFU]{{0,2}})"
    rf"(?P<quote>[\"'])(?!{re.escape(REDACTED)})(?P<value>[^\"'\n]{{4,}})(?P=quote)",
    re.IGNORECASE,
)


def redact_secrets(text: str) -> tuple[str, int]:
    """
    Replaces credentials in the text with [REDACTED]. Returns the text and how many
    values were replaced. Variable names and code structure are kept, so the model
    can still explain what the code does.
    """
    if not text:
        return text or "", 0

    total = 0
    for pattern, replacement in (
        (_PRIVATE_KEY_RE, REDACTED),
        (_TOKEN_RE, REDACTED),
        (_URL_CREDENTIALS_RE, REDACTED),
        (_ASSIGNMENT_RE, lambda m: f"{m.group('head')}{m.group('quote')}{REDACTED}{m.group('quote')}"),
    ):
        text, count = pattern.subn(replacement, text)
        total += count
    return text, total


def redact(text: str) -> str:
    """redact_secrets without the count."""
    cleaned, count = redact_secrets(text)
    if count:
        logger.info("Redacted %d secret value(s) before sending text to the cloud.", count)
    return cleaned
