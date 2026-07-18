import logging
from typing import Dict, Any
import time

from statements.models import Statement

# Import internal chatbot modules
from chatbot.intent import detect_intent
from chatbot.retrieval import build_context
from chatbot.prompt_builder import build_prompt
from chatbot.ai import generate_response

logger = logging.getLogger(__name__)


def chat_with_statement(statement_id: int, message: str, user=None) -> Dict[str, Any]:
    """
    Orchestrates the chatbot pipeline without containing business logic itself.
    Flow:
    1. Retrieve the Statement object.
    2. Detect intent and extract entities.
    3. Pass statement and entities to retrieval engine.
    4. Pass retrieved context and user message to prompt builder.
    5. Generate the AI response.
    """
    try:
        start = time.perf_counter()
        
        # 1. Retrieve the Statement object
        try:
            if user:
                statement = Statement.objects.prefetch_related("transactions").get(id=statement_id, user=user)
            else:
                statement = Statement.objects.prefetch_related("transactions").get(id=statement_id)
        except Statement.DoesNotExist:
            logger.warning(f"Chatbot failed: Statement {statement_id} not found.")
            return {
                "success": False,
                "status_code": 404,
                "message": "Statement not found."
            }

        # 2. Call the intent detector
        # Unpacking assumes detect_intent returns a tuple: (intent_enum_or_str, entities_dict)
        intent, entities = detect_intent(message)
        logger.info(f"Chatbot processing statement {statement_id} with intent: {intent}")

        # 3. Retrieve structured context
        context = build_context(
            statement=statement,
            intent=intent,
            entities=entities
        )

        # 4. Build the final prompt
        prompt = build_prompt(
            user_message=message,
            context=context
        )

        # 5. Generate response from AI service
        answer = generate_response(
            prompt=prompt, 
            user_message=message
        )

        if not answer:
            logger.warning(f"AI service returned an empty or invalid response for statement {statement_id}.")
            return {
                "success": False,
                "status_code": 500,
                "message": "Unable to generate a response at the moment."
            }

        logger.info(
            "Chat processed in %.2f ms",
            (time.perf_counter() - start) * 1000
        )

        # 6. Return structured dictionary
        return {
            "success": True,
            "answer": answer,
            "intent": intent.value if hasattr(intent, "value") else intent
        }

    except Exception as e:
        # Catch exceptions, log them safely, never expose stack traces to user
        logger.exception("Unexpected error in chatbot pipeline for statement %s", statement_id)
        return {
            "success": False,
            "status_code": 500,
            "message": "An unexpected error occurred while processing your request. Please try again later."
        }
