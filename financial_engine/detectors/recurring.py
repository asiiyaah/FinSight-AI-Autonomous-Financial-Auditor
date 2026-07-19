from typing import List, Dict

def detect_recurring_patterns(transactions: List[Dict], amount_tolerance: float = 0.05, min_occurrences: int = 2) -> List[Dict]:
    """
    Detects recurring payment patterns across months.
    
    Groups transactions by normalized_vendor.
    Allows for minor variance in amount (amount_tolerance).
    Requires the pattern to appear in at least min_occurrences unique months.
    
    Expected transaction format:
    {
        "id": int (optional),
        "date": datetime.date,
        "vendor": str,
        "normalized_vendor": str,
        "amount": float,
        "category": str,
        "raw_description": str
    }
    
    Returns a list of recurring groups.
    """
    groups = {}
    
    # Group by normalized vendor first
    for tx in transactions:
        vendor = tx.get("normalized_vendor", tx["vendor"])
        if vendor not in groups:
            groups[vendor] = []
        groups[vendor].append(tx)
        
    recurring_patterns = []
    
    for vendor, txs in groups.items():
        if len(txs) < min_occurrences:
            continue
            
        # Sort by date
        txs.sort(key=lambda x: x["date"])
        
        # Sub-group by amount (with tolerance)
        amount_groups = []
        for tx in txs:
            placed = False
            for ag in amount_groups:
                base_amount = ag[0]["amount"]
                diff = abs(tx["amount"] - base_amount)
                if base_amount > 0 and diff / base_amount <= amount_tolerance:
                    ag.append(tx)
                    placed = True
                    break
            if not placed:
                amount_groups.append([tx])
                
        for ag in amount_groups:
            if len(ag) < min_occurrences:
                continue
                
            # Check unique months
            unique_months = set()
            for tx in ag:
                unique_months.add((tx["date"].year, tx["date"].month))
                
            if len(unique_months) >= min_occurrences:
                avg_amount = sum(t["amount"] for t in ag) / len(ag)
                recurring_patterns.append({
                    "vendor": vendor,
                    "original_vendor": ag[0]["vendor"],
                    "average_amount": avg_amount,
                    "occurrences": len(ag),
                    "months_detected": len(unique_months),
                    "category": ag[0].get("category", "Uncategorized"),
                    "transactions": ag,
                    "source": "deterministic",
                    "confidence": 0.85 + min(0.1, 0.02 * len(unique_months)), # higher confidence with more months
                    "reason": f"Recurring payment detected across {len(unique_months)} months"
                })
                
    return recurring_patterns
