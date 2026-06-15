from pydantic import BaseModel
from typing import List , Literal


class AIAuditSchema(BaseModel):
    """
    Structured schema for Layer B AI audit output.

    Purpose:
    Enforce consistent Gemini response format for:
    - backend validation
    - database storage
    - frontend rendering
    """
    
    risk_level: Literal["LOW" , "MODERATE" , "HIGH"]
    overall_summary: str
    strengths: List[str]
    concerns: List[str]
    suspicious_activity: List[str]
    recommendations: List[str]  
    final_verdict: str