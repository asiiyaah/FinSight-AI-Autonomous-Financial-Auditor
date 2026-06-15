import json


def build_audit_prompt(ai_context):
    """
    Build the prompt for Gemini financial auditing.

    Purpose:
    Provide Gemini with:
    - compressed financial analytics
    - audit instructions
    - reasoning constraints
    - expected JSON output format
    """

    prompt = f"""
    You are an expert financial statement auditor.

    Your task is to analyze structured bank statement analytics and generate a professional audit report.

    Analyze the following:
    1. Cashflow health
    2. Spending behavior
    3. Financial risks
    4. Suspicious transaction patterns
    5. Practical recommendations

    Rules:
    - Use ONLY the provided analytics.
    - Do NOT assume facts not present in input.
    - Do NOT hallucinate missing details.
    - Be objective and auditor-like.
    - Recommendations must be practical and specific.

    Formatting rules:
  - Keep overall_summary under 120 words.
  - Keep final_verdict under 80 words.
  - Each bullet point must be concise (maximum 25 words).
  - Avoid repeating the same insight across multiple sections unless necessary.
  - If no suspicious activity exists, return an empty list [] for suspicious_activity.
  - Do NOT write phrases like "No suspicious activity detected" inside suspicious_activity.
  - Return 2-4 strengths.
  - Return 2-4 concerns.
  - Return 0-3 suspicious activities.
  - Return 2-4 recommendations.    

    Risk level must be EXACTLY one of:
    LOW
    MODERATE
    HIGH

    Return valid JSON only in this format:

    {{  
  "risk_level": "LOW | MODERATE | HIGH",
  "overall_summary": "...",
  "strengths": ["..."],
  "concerns": ["..."],
  "suspicious_activity": ["..."],
  "recommendations": ["..."],
  "final_verdict": "..."
    }}

    Analytics to audit:
    {json.dumps(ai_context, indent=2)}
    """
    
    return prompt
