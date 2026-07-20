import logging
from typing import Optional

logger = logging.getLogger(__name__)

def generate_response(prompt: str) -> str:
    """
    Sends the fully constructed prompt to the Gemini API and returns the raw text.
    """
    from services.llm import get_llm_provider
    from services.llm.exceptions import LLMError
    
    provider = get_llm_provider(operation="chatbot")
    
    try:
        response_text = provider.generate_content(prompt=prompt)
        if response_text:
            return response_text
        else:
            logger.warning("LLM Provider returned an empty or invalid response.")
            return "I couldn't find enough information in this statement to answer that."
            
    except LLMError as e:
        # Let the view handle the specific LLMError for consistent JSON responses
        raise e
    except Exception as e:
        logger.error(f"Unexpected Chatbot AI Exception: {str(e)}")
        raise e
