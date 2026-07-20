from typing import Dict, Any

def get_anomaly_context(analytics: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Returns unusual high-value transactions and potential duplicate charges.
    """
    risks = analytics.get("risks", {})
    return {
        "intent": "ANOMALY",
        "anomalies": risks.get("anomalies", []),
        "duplicates": risks.get("duplicates", [])
    }
