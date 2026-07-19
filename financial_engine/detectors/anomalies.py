from typing import List, Dict
import numpy as np

MIN_ANOMALY_SAMPLE_SIZE = 10
PENALTY_KEYWORDS = ["penalty", "bounce", "overdraft", "late fee", "fine", "insufficient"]

def detect_anomalies(transactions: List[Dict]) -> List[Dict]:
    """
    Detects anomalous transactions using a combination of statistical IQR
    and financial rule-based heuristics.
    """
    anomalies = []
    
    debits = [tx for tx in transactions if tx.get("transaction_type") == "debit"]
    
    # 1. Statistical Anomalies (IQR instead of Std Dev)
    if len(debits) >= MIN_ANOMALY_SAMPLE_SIZE:
        amounts = [float(tx["amount"]) for tx in debits]
        q1 = np.percentile(amounts, 25)
        q3 = np.percentile(amounts, 75)
        iqr = q3 - q1
        
        # Define high threshold (e.g., Q3 + 2.0 * IQR)
        # Using a slightly higher multiplier than standard 1.5 for financial transactions
        # to avoid flagging regular large expenses like rent.
        threshold = q3 + (2.0 * iqr)
        
        # Ensure threshold is at least a meaningful value
        threshold = max(threshold, 2000.0) 
        
        for tx in debits:
            amt = float(tx["amount"])
            if amt > threshold:
                # Add anomaly if not already categorized as Rent or EMI where large amounts are expected
                if tx.get("category") not in ["Rent", "EMI"]:
                    anomalies.append({
                        "id": tx.get("id"),
                        "date": str(tx["date"]),
                        "vendor": tx.get("normalized_vendor", tx["vendor"]),
                        "amount": amt,
                        "category": tx.get("category"),
                        "type": "statistical",
                        "source": "deterministic",
                        "confidence": 0.8,
                        "reason": f"Amount is unusually high compared to typical spending (Threshold: {round(threshold, 2)})"
                    })
                    
    # 2. Rule-based Anomalies
    for tx in debits:
        amt = float(tx["amount"])
        vendor = tx.get("normalized_vendor", tx["vendor"]).lower()
        raw = tx.get("raw_description", "").lower()
        
        # a) Penalty charges
        if any(kw in vendor or kw in raw for kw in PENALTY_KEYWORDS):
            anomalies.append({
                "id": tx.get("id"),
                "date": str(tx["date"]),
                "vendor": vendor,
                "amount": amt,
                "category": tx.get("category"),
                "type": "rule_penalty",
                "source": "deterministic",
                "confidence": 0.95,
                "reason": "Transaction identified as a penalty or fee."
            })
            
        # b) Large ATM withdrawals
        if "atm" in vendor or "atm" in raw or "cash withdrawal" in raw:
            if amt >= 10000:
                anomalies.append({
                    "id": tx.get("id"),
                    "date": str(tx["date"]),
                    "vendor": vendor,
                    "amount": amt,
                    "category": tx.get("category"),
                    "type": "rule_atm",
                    "source": "deterministic",
                    "confidence": 0.9,
                    "reason": "Unusually large ATM/Cash withdrawal."
                })
                
    # Deduplicate anomalies if a transaction was flagged multiple times
    seen_ids = set()
    unique_anomalies = []
    for anom in anomalies:
        tx_id = anom.get("id")
        if tx_id:
            if tx_id not in seen_ids:
                seen_ids.add(tx_id)
                unique_anomalies.append(anom)
        else:
            unique_anomalies.append(anom)
            
    return unique_anomalies
