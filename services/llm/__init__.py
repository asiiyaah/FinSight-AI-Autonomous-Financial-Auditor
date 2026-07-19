from .exceptions import (
    LLMError,
    LLMQuotaError,
    LLMRateLimitError,
    LLMAuthenticationError,
    LLMNetworkError,
    LLMProviderError
)
from .provider import LLMProvider
from .gemini import GeminiProvider

def get_llm_provider(operation="unknown", statement_id=None, user_id=None) -> LLMProvider:
    """Factory to get the currently configured LLM provider."""
    # In the future, this can check settings.LLM_PROVIDER to return Groq, OpenRouter, etc.
    return GeminiProvider(
        operation=operation,
        statement_id=statement_id,
        user_id=user_id
    )
