from typing import List, Dict
from financial_engine.config import CONFIDENCE_WEIGHTS
import datetime

BILL_KEYWORDS = ["kseb", "electricity", "water", "broadband", "gas", "utility", "rent", "telecom", "jio", "airtel"]
BILL_CATEGORIES = ['Utilities', 'Rent', 'Bills']

def detect_recurring_bills(transactions: List[Dict], context: Dict) -> List[Dict]:
    """
    Detects recurring bills (utilities, rent) to distinguish them from entertainment subscriptions.
    """
    debits = [tx for tx in transactions if tx.get("transaction_type") == "debit"]
    
    # Group by normalized vendor
    groups = {}
    for tx in debits:
        vendor = tx.get("normalized_vendor", tx["vendor"])
        if vendor not in groups:
            groups[vendor] = []
        groups[vendor].append(tx)
        
    bills = []
    
    for vendor, txs in groups.items():
        sample_tx = txs[0]
        category = sample_tx.get("category", "Uncategorized")
        raw_text = " ".join([t.get("raw_description", "") for t in txs]).lower()
        original_vendor = sample_tx.get("vendor", vendor)
        
        confidence = 0.0
        reasons = []
        
        # 1. Category Match
        if category in BILL_CATEGORIES:
            confidence += CONFIDENCE_WEIGHTS["category_match"]
            reasons.append(f"Category '{category}' strongly indicates a recurring bill")
            
        # 2. Keyword Match
        if any(kw in vendor.lower() for kw in BILL_KEYWORDS) or any(kw in raw_text for kw in BILL_KEYWORDS):
            confidence += CONFIDENCE_WEIGHTS["keyword_match"]
            reasons.append("Contains bill/utility-related keywords")
            
        # Ensure we only enrich if there's already some evidence
        if confidence > 0:
            # 3. Recurrence Check (Enrichment)
            unique_months = set((tx["date"].year, tx["date"].month) for tx in txs if isinstance(tx.get("date"), datetime.date))
            months_detected = len(unique_months)
            
            if months_detected >= 2:
                confidence += CONFIDENCE_WEIGHTS["recurring_enrichment"]
                reasons.append(f"Recurring pattern over {months_detected} months")
                
        # Final Classification (Threshold 0.40)
        if confidence >= 0.40:
            avg_amount = sum(float(t["amount"]) for t in txs) / len(txs)
            bills.append({
                "vendor": original_vendor,
                "normalized_vendor": vendor,
                "amount": avg_amount,
                "occurrences": len(txs),
                "months_detected": months_detected,
                "category": category,
                "confidence": min(0.99, confidence),
                "source": "deterministic",
                "reason": " | ".join(reasons)
            })
            
    return bills
