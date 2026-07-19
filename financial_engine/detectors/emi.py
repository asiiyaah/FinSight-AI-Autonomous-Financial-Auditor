from typing import List, Dict
from financial_engine.config import CONFIDENCE_WEIGHTS, THRESHOLDS
import datetime
import re

EMI_KEYWORDS = ["emi", "loan", "finance", "installment", "ecs", "repayment", "credit loan", "home loan", "auto loan", "personal loan"]
EMI_CATEGORIES = ['EMI', 'Credit Card Bill', 'Loan']

def detect_emi(transactions: List[Dict], context: Dict) -> Dict:
    """
    Detects EMI and Loan repayments by evaluating merchant category, keywords, and recurrence.
    """
    debits = [tx for tx in transactions if tx.get("transaction_type") == "debit"]
    
    # Group by normalized vendor
    groups = {}
    for tx in debits:
        vendor = tx.get("normalized_vendor", tx["vendor"])
        if vendor not in groups:
            groups[vendor] = []
        groups[vendor].append(tx)
        
    loans = []
    total_monthly_emi = 0
    
    for vendor, txs in groups.items():
        sample_tx = txs[0]
        category = sample_tx.get("category", "Uncategorized")
        raw_text = " ".join([t.get("raw_description", "") for t in txs]).lower()
        original_vendor = sample_tx.get("vendor", vendor)
        
        confidence = 0.0
        reasons = []
        
        # 1. Category Match
        if category in EMI_CATEGORIES:
            confidence += CONFIDENCE_WEIGHTS["category_match"]
            reasons.append(f"Category '{category}' strongly indicates loan/EMI")
            
        # 2. Keyword Match
        keyword_matched = False
        for kw in EMI_KEYWORDS:
            if re.search(r'\b' + re.escape(kw) + r'\b', vendor.lower()) or re.search(r'\b' + re.escape(kw) + r'\b', raw_text):
                keyword_matched = True
                break
                
        if keyword_matched:
            confidence += CONFIDENCE_WEIGHTS["keyword_match"]
            reasons.append("Contains EMI/Loan-related keywords")
            
        # Ensure we only enrich if there's already some evidence
        if confidence > 0:
            # 3. Recurrence Check (Enrichment)
            unique_months = set((tx["date"].year, tx["date"].month) for tx in txs if isinstance(tx.get("date"), datetime.date))
            months_detected = len(unique_months)
            
            if months_detected >= 2:
                confidence += CONFIDENCE_WEIGHTS["recurring_enrichment"]
                reasons.append(f"Recurring pattern over {months_detected} months")
            
        # Final Classification
        if confidence >= THRESHOLDS["emi_min_confidence"]:
            avg_amount = sum(float(t["amount"]) for t in txs) / len(txs)
            loans.append({
                "vendor": original_vendor,
                "normalized_vendor": vendor,
                "amount": avg_amount,
                "months_detected": months_detected,
                "confidence": min(0.99, confidence),
                "source": "deterministic",
                "reason": " | ".join(reasons)
            })
            total_monthly_emi += avg_amount
            
    return {
        "detected": len(loans) > 0,
        "total_monthly_emi": total_monthly_emi,
        "loans": loans
    }
