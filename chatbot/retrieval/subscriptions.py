from typing import Dict, Any

def get_subscription_context(analytics: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Returns detected recurring subscriptions.
    """
    risks = analytics.get("risks", {})
    subs = risks.get("subscriptions", [])
    
    total = sum(sub.get("amount", 0) for sub in subs)
    
    return {
        "intent": "SUBSCRIPTION",
        "aggregates": {
            "count": len(subs),
            "total_monthly": total
        },
        "subscriptions": subs
    }
    
def get_emi_context(analytics: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Returns detected loan/EMI obligations.
    """
    risks = analytics.get("risks", {})
    emi = risks.get("emi", {})
    
    return {
        "intent": "EMI",
        "aggregates": {
            "total_monthly_emi": emi.get("total_monthly_emi", 0),
            "count": len(emi.get("loans", []))
        },
        "emi": emi
    }
