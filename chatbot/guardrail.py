import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Phrase patterns for Guardrail detection
ILLEGAL_PATTERNS = [
    r"\bhack\b", r"\bfraud", r"\billegal\b", r"\blaunder", r"money laundering",
    r"tax evasion", r"forge", r"bypassing kyc", r"steal", r"access another person",
    r"malware", r"\btransfer\b"
]

PROMPT_INJECTION_PATTERNS = [
    r"ignore previous", r"reveal your system prompt", r"print hidden",
    r"forget you're", r"act as", r"ignore instructions", r"system prompt",
    r"ignore your instructions"
]

IRRELEVANT_PATTERNS = [
    r"\bjoke\b", r"weather", r"who won", r"python", r"machine learning",
    r"resume", r"prime minister", r"virat kohli", r"who is"
]

FINANCIAL_ADVICE_PATTERNS = [
    r"stock should i buy", r"guarantee profit", r"tomorrow'?s market",
    r"invest in", r"crypto", r"bitcoin"
]

def validate_financial_query(message: str, statement_id: int) -> Tuple[bool, str, str]:
    """
    Validates a query using rule-based classifiers.
    Returns (is_valid, category, fallback_response)
    """
    msg_lower = message.lower()
    
    # 1. Illegal Activity
    if any(re.search(pattern, msg_lower) for pattern in ILLEGAL_PATTERNS):
        logger.warning(f"Guardrail Blocked [ILLEGAL]: Statement {statement_id} | Query: {message}")
        return False, "Illegal activity", "I can't assist with illegal or fraudulent financial activities."
        
    # 2. Prompt Injection
    if any(re.search(pattern, msg_lower) for pattern in PROMPT_INJECTION_PATTERNS):
        logger.warning(f"Guardrail Blocked [INJECTION]: Statement {statement_id} | Query: {message}")
        return False, "Prompt injection", "I am a financial assistant and must follow my core instructions."

    # 3. Irrelevant / General Knowledge
    if any(re.search(pattern, msg_lower) for pattern in IRRELEVANT_PATTERNS):
        logger.warning(f"Guardrail Blocked [IRRELEVANT]: Statement {statement_id} | Query: {message}")
        return False, "Irrelevant", "I'm designed to help analyze your uploaded financial statements. Please ask a question related to your statement or financial activity."

    # 4. Financial Advice
    if any(re.search(pattern, msg_lower) for pattern in FINANCIAL_ADVICE_PATTERNS):
        logger.warning(f"Guardrail Flagged [ADVICE]: Statement {statement_id} | Query: {message}")
        return False, "Financial advice", "I can provide general educational guidance based on your statement, but I cannot offer guaranteed profits or specific stock recommendations."
        
    return True, "Statement-related", ""
