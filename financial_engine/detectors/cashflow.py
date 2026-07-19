from typing import List, Dict

def calculate_cashflow(transactions: List[Dict]) -> Dict:
    total_credit = sum(tx["amount"] for tx in transactions if tx.get("transaction_type") == "credit")
    total_debit = sum(tx["amount"] for tx in transactions if tx.get("transaction_type") == "debit")
    net_savings = total_credit - total_debit
    savings_rate = (net_savings / total_credit * 100) if total_credit > 0 else 0
    
    return {
        "total_credit": float(total_credit),
        "total_debit": float(total_debit),
        "net_savings": float(net_savings),
        "savings_rate": round(float(savings_rate), 2),
        "source": "deterministic",
        "confidence": 1.0,
        "reason": "Calculated deterministically from statement transactions."
    }
