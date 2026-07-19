import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def _generate_mock_response(user_message: str) -> str:
    """
    Returns a mock AI response for local development without using API credits.
    Uses basic substring matching against the user's actual message to return somewhat contextual placeholder text.
    """
    msg_lower = user_message.lower()
    
    if "food" in msg_lower or "dining" in msg_lower or "restaurant" in msg_lower:
        return "Based on the available statement data, your food expenses total ₹8,420."
    elif "recommendation" in msg_lower or "advice" in msg_lower or "improve" in msg_lower:
        return "Your spending is generally healthy. Consider reducing discretionary shopping and increasing monthly savings."
    elif "subscription" in msg_lower or "netflix" in msg_lower or "prime" in msg_lower:
        return "You have several active subscriptions detected in the statement. Review them to see if any can be canceled to increase savings."
    elif "anomaly" in msg_lower or "unusual" in msg_lower:
        return "There is one unusual high-value transaction of ₹45,000. Please verify this purchase."
    elif "cashflow" in msg_lower or "balance" in msg_lower:
        return "Your net savings for this period are positive. You have earned more than you spent."
        
    return "This is a mock AI response. To get real financial insights, disable USE_MOCK_AI in your configuration and ensure GEMINI_API_KEY is set."


def _generate_gemini_response(prompt: str) -> str:
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
            return "I'm sorry, I couldn't generate a meaningful response based on that data."
            
    except LLMError as e:
        # Let the view handle the specific LLMError for consistent JSON responses
        raise e
    except Exception as e:
        logger.error(f"Unexpected Chatbot AI Exception: {str(e)}")
        return "I'm unable to generate a response right now. Please try again in a moment."


def generate_response(prompt: str, user_message: str = "") -> str:
    """
    Main entry point for the AI service layer.
    Routes to either Mock AI or Gemini based on project configuration.
    Accepts user_message separately so the mock AI can inspect it without getting confused by prompt context.
    Never modifies the prompt or accesses the database.
    """
    # Check Django settings for mock AI configuration
    use_mock = getattr(settings, 'USE_MOCK_AI', True) or not getattr(settings, 'GEMINI_API_KEY', None)
        
    if use_mock:
        return _generate_mock_response(user_message)
    else:
        return _generate_gemini_response(prompt)
