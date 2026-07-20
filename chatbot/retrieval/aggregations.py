from typing import Dict, Any, List
from django.db.models import QuerySet

def compute_aggregates(transactions: QuerySet) -> Dict[str, Any]:
    """
    Computes exact statistical aggregations natively in Python so the LLM doesn't have to calculate.
    """
    if not transactions:
        return {
            "total": 0.0,
            "count": 0,
            "average": 0.0,
            "max": None,
            "min": None
        }

    total = sum(tx.amount for tx in transactions)
    count = len(transactions)
    average = total / count if count > 0 else 0.0
    
    # Max / Min
    sorted_txs = sorted(transactions, key=lambda x: x.amount, reverse=True)
    max_tx = sorted_txs[0]
    min_tx = sorted_txs[-1]
    
    # Date Range
    dates = [tx.date for tx in transactions if tx.date]
    date_range = None
    if dates:
        dates.sort()
        date_range = {"start": str(dates[0]), "end": str(dates[-1])}
        
    return {
        "total": float(total),
        "count": count,
        "average": float(average),
        "max": {
            "amount": float(max_tx.amount),
            "vendor": max_tx.vendor,
            "date": str(max_tx.date)
        },
        "min": {
            "amount": float(min_tx.amount),
            "vendor": min_tx.vendor,
            "date": str(min_tx.date)
        },
        "date_range": date_range
    }
