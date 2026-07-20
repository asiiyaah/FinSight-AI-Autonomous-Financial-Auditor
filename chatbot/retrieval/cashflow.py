from typing import Dict, Any

def get_cashflow_context(analytics: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Returns cashflow metrics (total credit, total debit, net savings).
    """
    return {
        "intent": "CASHFLOW",
        "cashflow": analytics.get("cashflow", {})
    }
