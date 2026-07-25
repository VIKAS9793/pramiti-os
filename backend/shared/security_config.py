"""
security_config.py — Enterprise Security Guard for Pramiti OS

Responsibilities:
1. Validates required environment variables on startup (fail-fast).
2. Enforces the ENVIRONMENT flag to block cloud API usage in production.
3. Provides a prompt injection detection utility used by all agent nodes.
4. Logs security violations with stable, structured log strings (no PII).

This module MUST be imported and called before any LLM node executes.
"""
import os
import re
import logging
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("pramiti_os.security")

# ---------------------------------------------------------------------------
# 1. REQUIRED ENVIRONMENT VARIABLES
# ---------------------------------------------------------------------------
REQUIRED_ENV_VARS = [
    "GROQ_API_KEY",
    "APP_SECRET_KEY",
    "ENVIRONMENT",
]

PRODUCTION_BLOCKED_VARS = [
    "GROQ_API_KEY",  # Cloud inference is strictly forbidden in production
]

# ---------------------------------------------------------------------------
# 2. PROMPT INJECTION ATTACK PATTERNS
# These patterns cover common adversarial attack vectors against LLM pipelines.
# Reference: OWASP Top 10 for LLM Applications (LLM01: Prompt Injection)
# ---------------------------------------------------------------------------
INJECTION_PATTERNS = [
    # Direct instruction hijacking
    r"ignore\s+(all\s+|previous\s+|above\s+|prior\s+)*(previous\s+|all\s+)?instructions",
    r"forget (all |previous |above |prior )?instructions",
    r"disregard (all |previous |above |prior )?instructions",
    r"you are now",
    r"new persona",
    r"act as (a |an )?(?!relationship manager|rm|portfolio)",  # Allow RM role refs
    # Jailbreaks
    r"developer mode",
    r"DAN mode",
    r"jailbreak",
    r"bypass (safety|compliance|guardrail)",
    # System prompt extraction
    r"(repeat|print|reveal|show|output) (your |the )?(system prompt|instructions|rules)",
    r"what are your instructions",
    # Financial manipulation
    r"(approve|execute|confirm) (this |the )?(trade|transaction|reallocation) (without|bypass)",
    r"skip (the |human )?(approval|review|interrupt)",
    # Data exfiltration — allow optional words between verb and target
    r"(send|email|share|export)[\w\s]*(client|portfolio|pii|pan)[\w\s]*(data|details|info)",
]

_compiled_patterns = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


# ---------------------------------------------------------------------------
# 3. STARTUP VALIDATION (call once on import)
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def validate_environment() -> None:
    """
    Validates all required environment variables are present.
    Blocks cloud API usage in production environments.
    Raises EnvironmentError on failure — intentionally halts the process.
    """
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {missing}. "
            "Copy backend/.env.example to backend/.env and fill in your values."
        )

    env = os.getenv("ENVIRONMENT", "development").lower()
    if env == "production":
        for var in PRODUCTION_BLOCKED_VARS:
            if os.getenv(var):
                raise EnvironmentError(
                    f"SECURITY VIOLATION: {var} is set in a PRODUCTION environment. "
                    "Cloud API keys are forbidden in production (DPDP compliance). "
                    "Remove the key and use the on-premise vLLM endpoint instead."
                )
    logger.info("security_config.validate_environment.passed", extra={"env": env})


# ---------------------------------------------------------------------------
# 4. PROMPT INJECTION SCANNER
# ---------------------------------------------------------------------------
def scan_for_injection(user_input: str) -> bool:
    """
    Scans user-supplied input for known prompt injection attack patterns.

    Args:
        user_input: The raw string input from the RM's chat interface.

    Returns:
        True if a threat is detected, False if input is safe.

    Usage:
        if scan_for_injection(user_query):
            raise ValueError("Potential prompt injection detected. Request blocked.")
    """
    for pattern in _compiled_patterns:
        if pattern.search(user_input):
            # Log with a stable, structured string — no raw user input in logs (prevents log injection)
            logger.warning(
                "security_config.prompt_injection_detected",
                extra={"pattern": pattern.pattern[:50]},
            )
            return True
    return False


# ---------------------------------------------------------------------------
# 5. SAFE API KEY ACCESSOR
# ---------------------------------------------------------------------------
def get_groq_api_key() -> str:
    """
    Returns the Groq API key from the environment.
    Raises EnvironmentError if not set or if running in production.
    """
    validate_environment()
    key = os.getenv("GROQ_API_KEY", "")
    if not key or key.startswith("REPLACE_WITH"):
        raise EnvironmentError(
            "GROQ_API_KEY is not configured. "
            "Set it in backend/.env — see backend/.env.example."
        )
    return key
