class LLMError(Exception):
    """Base exception for all LLM provider errors."""
    status_code = 503

    def __init__(self, message, original_exception=None, provider=None, operation=None):
        super().__init__(message)
        self.original_exception = original_exception
        self.provider = provider
        self.operation = operation

class LLMQuotaError(LLMError):
    """Raised when the API daily/monthly quota is exhausted."""
    status_code = 429

    def __init__(self, message="AI service daily quota reached.", **kwargs):
        super().__init__(message, **kwargs)

class LLMRateLimitError(LLMError):
    """Raised when temporary rate limits are exceeded (HTTP 429 without quota exhausted, 503, etc)."""
    status_code = 503

    def __init__(self, message="AI service is temporarily busy. Please try again in a few moments.", **kwargs):
        super().__init__(message, **kwargs)

class LLMAuthenticationError(LLMError):
    """Raised when the API key is invalid or unauthorized."""
    status_code = 503

    def __init__(self, message="AI service configuration is invalid. Please contact the administrator.", **kwargs):
        super().__init__(message, **kwargs)

class LLMNetworkError(LLMError):
    """Raised when there is a connection/timeout error reaching the provider."""
    status_code = 503

    def __init__(self, message="Unable to reach the AI service. Please check your internet connection and try again.", **kwargs):
        super().__init__(message, **kwargs)

class LLMProviderError(LLMError):
    """Raised for any other generic provider error (e.g. invalid request, schema error)."""
    status_code = 502

    def __init__(self, message="AI service is temporarily unavailable. Please try again later.", **kwargs):
        super().__init__(message, **kwargs)
