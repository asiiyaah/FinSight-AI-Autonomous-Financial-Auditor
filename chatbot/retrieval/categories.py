from typing import Dict, Any

def get_category_context(analytics: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Returns the category breakdown and essential vs discretionary profile.
    """
    spending = analytics.get("spending", {})
    category_breakdown = spending.get("category_breakdown", {})
    
    entities = kwargs.get("entities") or {}
    requested_category = entities.get("category")
    
    if requested_category:
        # User is asking about a specific category (e.g. "Food")
        # Do not return the global breakdown. Only return if it exists.
        filtered_val = category_breakdown.get(requested_category)
        if filtered_val is not None:
            category_breakdown = {requested_category: filtered_val}
        else:
            category_breakdown = {}
            
        return {
            "intent": "CATEGORY",
            "category_breakdown": category_breakdown
        }

    return {
        "intent": "CATEGORY",
        "category_breakdown": category_breakdown,
        "spending_profile": spending.get("spending_profile", {})
    }
