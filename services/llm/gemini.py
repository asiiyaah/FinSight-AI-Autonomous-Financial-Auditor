import time
import logging
from django.conf import settings
from google import genai
from google.genai.errors import APIError
import google.generativeai as genai_old  # Fallback for chatbot if needed

from .provider import LLMProvider
from .exceptions import (
    LLMQuotaError,
    LLMRateLimitError,
    LLMAuthenticationError,
    LLMNetworkError,
    LLMProviderError,
    LLMError
)

logger = logging.getLogger(__name__)

class GeminiProvider(LLMProvider):
    def __init__(self, operation="unknown", statement_id=None, user_id=None, model="gemini-2.5-flash"):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = model
        self.operation = operation
        self.statement_id = statement_id
        self.user_id = user_id
        self.provider_name = "Gemini"

    def _log_error(self, e: Exception):
        logger.error(
            f"LLM Provider Error | Provider: {self.provider_name} | Model: {self.model} | "
            f"Operation: {self.operation} | Statement: {self.statement_id} | User: {self.user_id}\n"
            f"Error Details: {str(e)}",
            exc_info=True
        )

    def _classify_and_raise(self, e: Exception):
        """Classifies the exception and raises the appropriate provider-agnostic error."""
        error_str = str(e)
        
        # 1. Daily Quota Exhausted
        if any(keyword in error_str for keyword in [
            "GenerateRequestsPerDayPerProjectPerModel-FreeTier",
            "generate_content_free_tier_requests",
            "RESOURCE_EXHAUSTED"
        ]):
            raise LLMQuotaError(
                original_exception=e, provider=self.provider_name, operation=self.operation
            )
            
        # 2. Authentication Error
        if "API_KEY_INVALID" in error_str or "401" in error_str or "403" in error_str:
            raise LLMAuthenticationError(
                original_exception=e, provider=self.provider_name, operation=self.operation
            )
            
        # 3. Rate Limit / Transient
        if "429" in error_str or "503" in error_str or "RetryInfo" in error_str:
            raise LLMRateLimitError(
                original_exception=e, provider=self.provider_name, operation=self.operation
            )
            
        # 4. Network Errors (catch-all for connection-related issues)
        if "Connection" in error_str or "Timeout" in error_str or "ReadTimeout" in error_str:
            raise LLMNetworkError(
                original_exception=e, provider=self.provider_name, operation=self.operation
            )
            
        # 5. Generic Provider Error
        raise LLMProviderError(
            message=f"Gemini API Error: {error_str}",
            original_exception=e, provider=self.provider_name, operation=self.operation
        )

    def generate_content(self, prompt: str, schema=None, temperature=None):
        max_retries = 2
        retry_delay = 5

        config = {}
        if schema:
            config["response_mime_type"] = "application/json"
            config["response_schema"] = schema
        if temperature is not None:
            config["temperature"] = temperature

        for attempt in range(max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config
                )
                
                if schema:
                    if not response.parsed:
                        raise ValueError("Empty Gemini response or failed to parse schema")
                    return response.parsed.model_dump()
                else:
                    return response.text
                    
            except Exception as e:
                # Log the raw exception on the server
                self._log_error(e)
                
                try:
                    self._classify_and_raise(e)
                except LLMRateLimitError as rate_limit_e:
                    if attempt < max_retries:
                        logger.warning(f"Transient error with Gemini. Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    else:
                        raise rate_limit_e
