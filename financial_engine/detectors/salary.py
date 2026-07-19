from typing import List, Dict
from .recurring import detect_recurring_patterns

def detect_salary(transactions: List[Dict]) -> Dict:
    credits = [tx for tx in transactions if tx.get("transaction_type") == "credit"]
    recurring_credits = detect_recurring_patterns(credits, amount_tolerance=0.05, min_occurrences=1)
    
    salary_sources = []
    total_monthly_salary = 0
    
    for pattern in recurring_credits:
        # Check if amount is significant (e.g. > 10,000) or contains keywords
        vendor = pattern["vendor"].lower()
        original_vendor = pattern["original_vendor"].lower()
        is_salary = False
        
        if pattern["average_amount"] >= 10000:
            if "salary" in original_vendor or "payroll" in original_vendor or pattern["category"] == "Income":
                is_salary = True
            elif pattern["months_detected"] >= 2:
                # large recurring credits across multiple months usually indicate salary
                is_salary = True
                
        if is_salary:
            salary_sources.append({
                "employer": pattern["original_vendor"],
                "normalized_employer": pattern["vendor"],
                "amount": pattern["average_amount"],
                "months_detected": pattern["months_detected"],
                "confidence": min(0.99, pattern["confidence"] + 0.1),
                "source": "deterministic",
                "reason": "Classified as salary based on amount, frequency, and keywords."
            })
            total_monthly_salary += pattern["average_amount"]
            
    return {
        "detected": len(salary_sources) > 0,
        "total_monthly_salary": total_monthly_salary,
        "sources": salary_sources,
        "source": "deterministic",
        "confidence": 0.9,
        "reason": "Salary detection heuristic applied."
    }
