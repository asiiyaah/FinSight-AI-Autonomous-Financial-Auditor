from typing import List, Dict
from financial_engine.config import CONFIDENCE_WEIGHTS, THRESHOLDS
import datetime
import re

SUBSCRIPTION_KEYWORDS = ["autopay", "subscription", "prime", "netflix", "spotify", "premium", "membership", "cloud", "adobe", "microsoft", "apple", "jio fiber"]
SUBSCRIPTION_CATEGORIES = ['Subscription', 'Entertainment']

def detect_subscriptions(transactions: List[Dict], context: Dict) -> List[Dict]:
    """
    Detects subscriptions by evaluating merchant category, keywords, and recurrence.
    """
    debits = [tx for tx in transactions if tx.get("transaction_type") == "debit"]
    
    # Group by normalized vendor
    groups = {}
    for tx in debits:
        vendor = tx.get("normalized_vendor", tx["vendor"])
        if vendor not in groups:
            groups[vendor] = []
        groups[vendor].append(tx)
        
    subscriptions = []
    
    for vendor, txs in groups.items():
        sample_tx = txs[0]
        category = sample_tx.get("category", "Uncategorized")
        raw_text = " ".join([t.get("raw_description", "") for t in txs]).lower()
        original_vendor = sample_tx.get("vendor", vendor)
        
        confidence = 0.0
        reasons = []
        
        # 1. Category Match
        if category in SUBSCRIPTION_CATEGORIES:
            confidence += CONFIDENCE_WEIGHTS["category_match"]
            reasons.append(f"Category '{category}' strongly indicates subscription")
            
        # 2. Keyword Match
        keyword_matched = False
        for kw in SUBSCRIPTION_KEYWORDS:
            if re.search(r'\b' + re.escape(kw) + r'\b', vendor.lower()) or re.search(r'\b' + re.escape(kw) + r'\b', raw_text):
                keyword_matched = True
                break
                
        if keyword_matched:
            confidence += CONFIDENCE_WEIGHTS["keyword_match"]
            reasons.append("Contains subscription-related keywords")
            
        # Ensure we only enrich if there's already some evidence
        if confidence > 0:
            # 3. Recurrence Check (Enrichment)
            unique_months = set((tx["date"].year, tx["date"].month) for tx in txs if isinstance(tx.get("date"), datetime.date))
            months_detected = len(unique_months)
            
            if months_detected >= 2:
                confidence += CONFIDENCE_WEIGHTS["recurring_enrichment"]
                reasons.append(f"Recurring pattern over {months_detected} months")
            
            # If no strong signals, but lots of small transactions? (Optional heuristic)
            if months_detected >= 3 and confidence < 0.4:
                avg_amount = sum(float(t["amount"]) for t in txs) / len(txs)
                if avg_amount < 5000:
                    confidence += 0.4
                    reasons.append("Consistent repeating small payments")
                
        # Final Classification
        if confidence >= THRESHOLDS["subscription_min_confidence"]:
            avg_amount = sum(float(t["amount"]) for t in txs) / len(txs)
            subscriptions.append({
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
            
    return subscriptions
