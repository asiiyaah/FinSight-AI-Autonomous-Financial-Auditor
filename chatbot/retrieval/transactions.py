from typing import Dict, Any, Optional
from statements.models import Statement
from chatbot.retrieval.aggregations import compute_aggregates

def get_transaction_context(statement: Statement, entities: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
    """
    Retrieves specific transactions based on entities (merchant, date, category).
    Also returns computed aggregates.
    """
    transactions = statement.transactions.all()
    entities = entities or {}
    
    merchant = entities.get("merchant")
    category = entities.get("category")
    
    if merchant:
        matched_txs = list(transactions.filter(vendor__icontains=merchant))
    elif category:
        matched_txs = list(transactions.filter(category__icontains=category))
    else:
        # Default to top 20 largest debits if no filter
        matched_txs = list(transactions.filter(transaction_type="debit").order_by("-amount")[:20])

    data = []
    for tx in matched_txs:
        data.append({
            "date": str(tx.date),
            "vendor": tx.vendor,
            "amount": float(tx.amount),
            "category": tx.category,
            "type": tx.transaction_type
        })
        
    aggregates = compute_aggregates(matched_txs)
        
    return {
        "intent": "TRANSACTION",
        "aggregates": aggregates,
        "transactions": data
    }

def get_top_spending_context(statement: Statement, **kwargs) -> Dict[str, Any]:
    """
    Returns the top 10 highest debits in the statement.
    """
    matched_txs = list(statement.transactions.filter(transaction_type="debit").order_by("-amount")[:10])
    
    data = []
    for tx in matched_txs:
        data.append({
            "date": str(tx.date),
            "vendor": tx.vendor,
            "amount": float(tx.amount),
            "category": tx.category,
            "type": tx.transaction_type
        })
        
    aggregates = compute_aggregates(matched_txs)
        
    return {
        "intent": "TOP_SPENDING",
        "aggregates": aggregates,
        "top_spending": data
    }
