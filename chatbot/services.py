import logging
from typing import Dict, Any
import time
from django.core.cache import cache

from statements.models import Statement

# Import internal chatbot modules
from chatbot.guardrail import validate_financial_query
from chatbot.intent import detect_intent
from chatbot.retrieval import build_context
from chatbot.prompt_builder import build_prompt
from chatbot.ai import generate_response
from services.llm.exceptions import LLMError
from chatbot.enums import Intent

logger = logging.getLogger(__name__)

def generate_deterministic_fallback(context: Dict[str, Any], top_intent: Intent, entities: Dict[str, Any] = None) -> str:
    """
    Generates a rich text response natively in Python when the LLM is unavailable.
    """
    if not context or "aggregates" not in context:
        return "I'm temporarily unavailable. Please try again later."
        
    aggs = context["aggregates"]
    entities = entities or {}
    
    if top_intent == Intent.CATEGORY and "category_breakdown" in context and not entities.get("category"):
        lines = ["Your highest spending categories are:\n"]
        sorted_cats = sorted(context["category_breakdown"].items(), key=lambda x: x[1], reverse=True)[:5]
        for cat, amt in sorted_cats:
            lines.append(f"• {cat} – ₹{amt:,.2f}")
        return "\n".join(lines)
        
    elif (top_intent in [Intent.TRANSACTION, Intent.CATEGORY]) and "transactions" in context:
        txs = context["transactions"]
        if not txs:
            return "No transactions found."
        
        entity_name = entities.get("category") or entities.get("merchant") or ""
        lines = [f"Found {aggs.get('count', len(txs))} {entity_name} transactions totaling ₹{aggs.get('total', 0):,.2f}.\n".replace("  ", " ")]
        for tx in txs[:5]:
            lines.append(f"• {tx['date']}: {tx['vendor']} – ₹{tx['amount']:,.2f}")
        return "\n".join(lines)
        
    # Default fallback
    return f"I couldn't generate an AI summary right now due to a service error, but here is the data: Total: ₹{aggs.get('total', 0):,.2f}, Count: {aggs.get('count', 0)}."

def chat_with_statement(statement_id: int, message: str, user=None) -> Dict[str, Any]:
    """
    Orchestrates the chatbot pipeline without containing business logic itself.
    """
    try:
        start = time.perf_counter()
        
        # 1. Guardrail Validation
        is_valid, block_category, fallback_message = validate_financial_query(message, statement_id)
        if not is_valid:
            return {
                "success": False,
                "status_code": 400,
                "message": fallback_message
            }
        
        # 2. Retrieve the Statement object
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

        # 3. Conversation History & Focus (Cache)
        user_id = user.id if user else "anon"
        cache_key = f"chat_history_{user_id}_{statement_id}"
        cached_data = cache.get(cache_key, {"history": [], "focus": {}})
        history = cached_data.get("history", [])
        focus = cached_data.get("focus", {})

        # 4. Call the intent detector
        intents, entities = detect_intent(message, focus=focus)
        top_intent = intents[0][0] if intents else Intent.SUMMARY
        logger.info(f"Chatbot processing statement {statement_id} with intents: {intents}")

        # 5. Retrieve structured context
        context = build_context(
            statement=statement,
            intents=intents,
            entities=entities
        )

        # 6. Early Exit for Empty Retrieval
        # If the user asked for a specific entity (e.g. merchant or category) and we found nothing.
        if entities:
            if context.get("aggregates", {}).get("count", -1) == 0:
                entity_name = entities.get("merchant") or entities.get("category") or "matching"
                answer = f"I couldn't find any {entity_name} transactions in this statement."
                return {
                    "success": True,
                    "answer": answer,
                    "intent": top_intent.value if hasattr(top_intent, "value") else top_intent
                }
            if top_intent == Intent.CASHFLOW and "salary" in message.lower() and context.get("cashflow", {}).get("total_credit", 0) == 0:
                return {
                    "success": True,
                    "answer": "I couldn't find any salary deposits or income in this statement.",
                    "intent": top_intent.value if hasattr(top_intent, "value") else top_intent
                }

        # 7. Build the final prompt
        prompt = build_prompt(
            user_message=message,
            context=context,
            history=history
        )

        # 8. Generate response from AI service
        try:
            answer = generate_response(prompt=prompt)
        except LLMError as e:
            logger.warning("LLM Error in chatbot: %s", str(e))
            answer = generate_deterministic_fallback(context, top_intent, entities)
                
        if not answer:
            answer = "I couldn't find enough information in this statement to answer that."

        # 9. Save to history and update focus
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": answer})
        history = history[-10:] # Keep last 5 turns
        
        # Update focus based on the current entities and intent
        new_focus = {"intent_type": top_intent.value if hasattr(top_intent, "value") else str(top_intent)}
        if "merchant" in entities:
            new_focus["type"] = "merchant"
            new_focus["value"] = entities["merchant"]
        elif "category" in entities:
            new_focus["type"] = "category"
            new_focus["value"] = entities["category"]
        else:
            new_focus["type"] = "intent"
            
        cache.set(cache_key, {"history": history, "focus": new_focus}, timeout=3600)

        logger.info(
            "Chat processed in %.2f ms",
            (time.perf_counter() - start) * 1000
        )

        return {
            "success": True,
            "answer": answer,
            "intent": top_intent.value if hasattr(top_intent, "value") else top_intent
        }

    except Exception as e:
        logger.exception("Unexpected error in chatbot pipeline for statement %s", statement_id)
        return {
            "success": False,
            "status_code": 500,
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred while processing your request. Please try again later."
        }
