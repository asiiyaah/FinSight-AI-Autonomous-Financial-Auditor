from typing import List, Dict

def detect_duplicates(transactions: List[Dict]) -> List[List[Dict]]:
    """
    Detect possible duplicate charges.
    Groups by normalized vendor, exact date, and exact amount.
    """
    debits = [tx for tx in transactions if tx.get("transaction_type") == "debit"]
    groups = {}

    for tx in debits:
        normalized_vendor = tx.get("normalized_vendor", tx["vendor"])
        # Same vendor, date, and amount
        key = (tx["date"], normalized_vendor, float(tx["amount"]))

        if key in groups:
            groups[key].append(tx)
        else:
            groups[key] = [tx]

    duplicates = []
    for group in groups.values():
        if len(group) > 1:
            group_data = []
            for tx in group:
                group_data.append({
                    "id": tx.get("id"),
                    "date": str(tx["date"]),
                    "vendor": tx.get("normalized_vendor", tx["vendor"]),
                    "original_vendor": tx["vendor"],
                    "amount": float(tx["amount"]),
                    "category": tx.get("category"),
                    "raw_description": tx.get("raw_description", ""),
                    "source": "deterministic",
                    "confidence": 0.95,
                    "reason": "Exact match on date, amount, and normalized vendor."
                })
            duplicates.append(group_data)

    return duplicates
