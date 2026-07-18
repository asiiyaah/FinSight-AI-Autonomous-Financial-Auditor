from typing import Dict, Any, Optional, List, Callable
from statements.models import Statement
from chatbot.enums import Intent

def get_summary_context(statement: Statement, analytics: Dict[str, Any], ai_audit: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Returns high-level metadata and AI verdict for the statement.
    """
    # Enrich metadata with statement-level details without mutating the original dict
    metadata = {
        **analytics.get("audit_context", {}),
        "filename": statement.file_name,
        "uploaded_at": str(statement.uploaded_at),
    }
    
    return {
        "metadata": metadata,
        "ai_summary": {
            "overall_summary": ai_audit.get("overall_summary", ""),
            "final_verdict": ai_audit.get("final_verdict", "")
        }
    }

def get_cashflow_context(analytics: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Returns cashflow metrics (total credit, total debit, net savings).
    """
    return analytics.get("cashflow", {})

def get_category_context(analytics: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Returns the category breakdown and essential vs discretionary profile.
    """
    spending = analytics.get("spending", {})
    return {
        "category_breakdown": spending.get("category_breakdown", {}),
        "spending_profile": spending.get("spending_profile", {})
    }

def get_subscription_context(analytics: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Returns detected recurring subscriptions.
    """
    risks = analytics.get("risks", {})
    return {
        "subscriptions": risks.get("subscriptions", [])
    }

def get_emi_context(analytics: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Returns detected loan/EMI obligations.
    """
    risks = analytics.get("risks", {})
    return {
        "emi": risks.get("emi", {})
    }

def get_anomaly_context(analytics: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Returns unusual high-value transactions and potential duplicate charges.
    """
    risks = analytics.get("risks", {})
    return {
        "anomalies": risks.get("anomalies", []),
        "duplicates": risks.get("duplicates", [])
    }

def get_recommendation_context(ai_audit: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Returns strengths, concerns, and actionable AI recommendations.
    """
    return {
        "recommendations": ai_audit.get("recommendations", []),
        "strengths": ai_audit.get("strengths", []),
        "concerns": ai_audit.get("concerns", [])
    }

def get_transaction_context(statement: Statement, entities: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
    """
    Retrieves specific transactions based on entities (merchant, date, etc.).
    Falls back to top 10 largest debits if no filters apply.
    """
    transactions = statement.transactions.all()
    entities = entities or {}
    
    merchant = entities.get("merchant")
    
    if merchant:
        # Filter transactions matching the extracted merchant
        matched_txs = list(transactions.filter(vendor__icontains=merchant))
    else:
        # If no explicit filter is provided, default to top 10 largest debits
        matched_txs = list(transactions.filter(transaction_type="debit").order_by("-amount")[:10])

    data = []
    for tx in matched_txs:
        data.append({
            "date": str(tx.date),
            "vendor": tx.vendor,
            "amount": float(tx.amount),
            "category": tx.category,
            "type": tx.transaction_type
        })
        
    return {"transactions": data}

def get_top_spending_context(statement: Statement, **kwargs) -> Dict[str, Any]:
    """
    Returns the top 10 highest debits in the statement.
    """
    transactions = statement.transactions.filter(transaction_type="debit").order_by("-amount")[:10]
    data = []
    for tx in transactions:
        data.append({
            "date": str(tx.date),
            "vendor": tx.vendor,
            "amount": float(tx.amount),
            "category": tx.category,
            "type": tx.transaction_type
        })
        
    return {"top_spending": data}

# Handler Mapping: Maps intents to a list of functions that provide context
INTENT_HANDLERS: Dict[Intent, List[Callable]] = {
    Intent.SUMMARY: [
        get_summary_context, get_cashflow_context, get_category_context, 
        get_subscription_context, get_emi_context, get_anomaly_context
    ],
    Intent.CASHFLOW: [get_cashflow_context],
    Intent.CATEGORY: [get_category_context],
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

def build_context(statement: Statement, intent: Intent, entities: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Gathers only the relevant data needed to answer a user's question based on intent.
    Returns structured Python dictionaries.
    """
    context = {}
    
    analytics = statement.analytics or {}
    ai_audit = statement.ai_audit or {}
    
    # Safely get intent handlers or default to SUMMARY
    handlers = INTENT_HANDLERS.get(intent, INTENT_HANDLERS[Intent.SUMMARY])
    
    for handler in handlers:
        context.update(handler(
            statement=statement, 
            analytics=analytics, 
            ai_audit=ai_audit, 
            entities=entities
        ))
        
    return context
