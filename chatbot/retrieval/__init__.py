from typing import Dict, Any, Optional, List, Callable
from statements.models import Statement
from chatbot.enums import Intent

# Import all modules
from chatbot.retrieval.transactions import get_transaction_context, get_top_spending_context
from chatbot.retrieval.categories import get_category_context
from chatbot.retrieval.cashflow import get_cashflow_context
from chatbot.retrieval.subscriptions import get_subscription_context, get_emi_context
from chatbot.retrieval.anomalies import get_anomaly_context
from chatbot.retrieval.recommendations import get_recommendation_context, get_summary_context

# Handler Mapping: Maps intents to a list of functions that provide context
INTENT_HANDLERS: Dict[Intent, List[Callable]] = {
    Intent.SUMMARY: [
        get_summary_context, get_cashflow_context, get_category_context, 
        get_subscription_context, get_emi_context, get_anomaly_context
    ],
    Intent.CASHFLOW: [get_cashflow_context],
    Intent.CATEGORY: [get_category_context, get_transaction_context],
    Intent.SUBSCRIPTION: [get_subscription_context],
    Intent.EMI: [get_emi_context],
    Intent.ANOMALY: [get_anomaly_context],
    Intent.RECOMMENDATION: [get_recommendation_context],
    Intent.TRANSACTION: [get_transaction_context],
    Intent.TOP_SPENDING: [get_top_spending_context],
    Intent.SPENDING_ANALYSIS: [
        get_cashflow_context, get_category_context, 
        get_recommendation_context, get_summary_context
    ],
}

def build_context(statement: Statement, intents: List[Tuple[Intent, float]], entities: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Dynamically routes to the appropriate module based on detected intents.
    Supports multi-intent merging.
    """
    context = {}
    analytics = statement.analytics or {}
    ai_audit = statement.ai_audit or {}
    
    # We will process the top intent. If the second intent is within 0.15 confidence, process it too.
    active_intents = []
    if intents:
        top_intent, top_score = intents[0]
        active_intents.append(top_intent)
        
        if len(intents) > 1:
            second_intent, second_score = intents[1]
            if top_score - second_score <= 0.15:
                active_intents.append(second_intent)
    else:
        active_intents = [Intent.SUMMARY]
        
    for intent in active_intents:
        handlers = INTENT_HANDLERS.get(intent, [])
        for handler in handlers:
            # Generate the dictionary from the handler
            result = handler(
                statement=statement, 
                analytics=analytics, 
                ai_audit=ai_audit, 
                entities=entities
            )
            
            # Merge lists and dicts safely
            for key, value in result.items():
                if key not in context:
                    context[key] = value
                elif isinstance(value, list) and isinstance(context[key], list):
                    # For transactions and anomalies
                    for item in value:
                        if item not in context[key]:
                            context[key].append(item)
                elif isinstance(value, dict) and isinstance(context[key], dict):
                    context[key].update(value)
                    
    # Cap transactions at 30 if present
    if "transactions" in context and isinstance(context["transactions"], list):
        context["transactions"] = context["transactions"][:30]
        
    return context
