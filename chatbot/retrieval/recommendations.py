from typing import Dict, Any

def get_recommendation_context(ai_audit: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Returns strengths, concerns, and actionable AI recommendations.
    """
    return {
        "intent": "RECOMMENDATION",
        "recommendations": ai_audit.get("recommendations", []),
        "strengths": ai_audit.get("strengths", []),
        "concerns": ai_audit.get("concerns", [])
    }
    
def get_summary_context(statement, analytics: Dict[str, Any], ai_audit: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Returns high-level metadata and AI verdict for the statement.
    """
    metadata = {
        **analytics.get("audit_context", {}),
        "filename": statement.file_name,
        "uploaded_at": str(statement.uploaded_at),
    }
    
    return {
        "intent": "SUMMARY",
        "metadata": metadata,
        "ai_summary": {
            "overall_summary": ai_audit.get("overall_summary", ""),
            "final_verdict": ai_audit.get("final_verdict", "")
        }
    }
