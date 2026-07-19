from typing import List, Dict
from financial_engine.merchant_mapping import ESSENTIAL_CATEGORIES, DISCRETIONARY_CATEGORIES

def calculate_spending(transactions: List[Dict]) -> Dict:
    category_breakdown = {}
    
    for tx in transactions:
        if tx.get("transaction_type") == "debit":
            cat = tx.get("category", "Uncategorized")
            category_breakdown[cat] = category_breakdown.get(cat, 0.0) + float(tx["amount"])
            
    essential_spend = 0
    discretionary_spend = 0
    
    for category, amount in category_breakdown.items():
        if category in ESSENTIAL_CATEGORIES:
            essential_spend += amount
        elif category in DISCRETIONARY_CATEGORIES:
            discretionary_spend += amount
        else:
            discretionary_spend += amount
            
    total_spend = essential_spend + discretionary_spend
    
    essential_ratio = (essential_spend / total_spend * 100) if total_spend > 0 else 0
    discretionary_ratio = (discretionary_spend / total_spend * 100) if total_spend > 0 else 0
    
    return {
        "category_breakdown": category_breakdown,
        "spending_profile": {
            "essential_spend": round(float(essential_spend), 2),
            "discretionary_spend": round(float(discretionary_spend), 2),
            "essential_ratio": round(float(essential_ratio), 2),
            "discretionary_ratio": round(float(discretionary_ratio), 2)
        },
        "source": "deterministic",
        "confidence": 1.0,
        "reason": "Aggregated from categorized transactions."
    }
