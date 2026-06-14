from pydantic import BaseModel
from typing import List


class AIAuditSchema(BaseModel):
    overall_summary: str
    strengths: List[str]
    concerns: List[str]
    suspicious_activity: List[str]
    recommendations: List[str]
    final_verdict: str