from typing import List, Dict
from financial_engine.config import CONFIDENCE_WEIGHTS, THRESHOLDS
import datetime
import re

SUBSCRIPTION_KEYWORDS = ["autopay", "subscription", "prime", "netflix", "spotify", "premium", "membership", "cloud", "adobe", "microsoft", "jio fiber"]
KNOWN_SUBSCRIPTION_MERCHANTS = ["netflix", "spotify", "amazon prime", "hotstar", "jio fiber", "adobe", "microsoft"]
SHOPPING_MERCHANTS = ["apple", "amazon", "flipkart", "reliance digital", "croma", "myntra", "ajio"]
SUBSCRIPTION_CATEGORIES = ['Subscription', 'Entertainment']

def detect_subscriptions(transactions: List[Dict], context: Dict) -> List[Dict]:
    """
    Detects subscriptions by evaluating merchant category, keywords, and recurrence using a score system.
    Score >= 3 -> Subscription
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
        
        score = 0
        reasons = []
        
        vendor_lower = vendor.lower()
        
        # 1. Known Subscription Merchant
        is_known_sub = any(kw in vendor_lower for kw in KNOWN_SUBSCRIPTION_MERCHANTS)
        if is_known_sub:
            score += 3
            reasons.append("Known subscription merchant")
            
        # 2. Category Match
        if category in SUBSCRIPTION_CATEGORIES:
            score += 1
            if not is_known_sub:
                reasons.append(f"Category '{category}'")
                
        # 3. Shopping Merchant Penalty
        is_shopping = any(kw in vendor_lower for kw in SHOPPING_MERCHANTS)
        if is_shopping:
            score -= 3
            reasons.append("Shopping merchant (requires stronger recurrence)")
            
        # 4. Keyword Match (if not already known sub)
        if not is_known_sub:
            keyword_matched = False
            for kw in SUBSCRIPTION_KEYWORDS:
                if re.search(r'\b' + re.escape(kw) + r'\b', vendor_lower) or re.search(r'\b' + re.escape(kw) + r'\b', raw_text):
                    keyword_matched = True
                    break
            if keyword_matched:
                score += 1
                reasons.append("Contains subscription-related keywords")
                
        # 5. Recurrence Check
        unique_months = set((tx["date"].year, tx["date"].month) for tx in txs if isinstance(tx.get("date"), datetime.date))
        months_detected = len(unique_months)
        
        if months_detected >= 2:
            score += 2
            reasons.append("Recurring payment detected")
            
        # Final Classification
        if score >= 3:
            avg_amount = sum(float(t["amount"]) for t in txs) / len(txs)
            
            # Construct a clean reason for the UI (prioritize main reasons)
            if "Known subscription merchant" in reasons:
                ui_reason = "Known subscription merchant"
            elif "Recurring payment detected" in reasons:
                ui_reason = "Recurring payment detected"
            else:
                ui_reason = reasons[0] if reasons else "Detected via AI rules"
                
            subscriptions.append({
                "vendor": original_vendor,
                "normalized_vendor": vendor,
                "amount": avg_amount,
                "occurrences": len(txs),
                "months_detected": months_detected,
                "category": category,
                "confidence": 0.9, # Mapping old confidence concept, though we use score now
                "source": "deterministic",
                "reason": ui_reason
            })
            
    return subscriptions
