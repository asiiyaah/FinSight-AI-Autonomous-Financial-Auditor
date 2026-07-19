from typing import Dict, Any, List
import time
from services.llm import get_llm_provider
from audits.schemas import AIAuditSchema
from audits.prompts import build_audit_prompt
from django.conf import settings

def get_top_categories(category_breakdown, top_n=3):
    sorted_categories = sorted(
        category_breakdown.items(),
        key=lambda item: item[1],
        reverse=True
    )
    return sorted_categories[:top_n]

def build_ai_context(analytics: Dict[str, Any]):
    context = analytics["audit_context"]
    cashflow = analytics["cashflow"]
    spending = analytics["spending"]
    risks = analytics["risks"]

    # -------- Spending Summary --------
    category_breakdown = spending["category_breakdown"]
    top_categories = get_top_categories(category_breakdown)

    # -------- Duplicate Transactions --------
    duplicate_vendors = []
    duplicate_count = len(risks["duplicates"])

    for group in risks["duplicates"]:
        if group:
            duplicate_vendors.append(group[0]["original_vendor"])

    # -------- Subscriptions --------
    subscription_count = len(risks["subscriptions"])
    monthly_subscription_total = sum(
        sub.get("amount", 0) for sub in risks["subscriptions"]
    )
    subscription_vendors = [
        sub.get("original_vendor", sub.get("vendor")) for sub in risks["subscriptions"]
    ]

    # -------- Anomalies --------
    anomaly_count = len(risks["anomalies"])
    largest_anomaly = None
    largest_anomaly_vendor = None
    top_anomalies = []

    if anomaly_count > 0:
        largest = max(
            risks["anomalies"],
            key=lambda x: x["amount"],
        )
        largest_anomaly = largest["amount"]
        largest_anomaly_vendor = largest["vendor"]
        sorted_anomalies = sorted(
            risks["anomalies"],
            key=lambda x: x["amount"],
            reverse=True
        )
        top_anomalies = sorted_anomalies[:3]

    # -------- Final Compressed Context --------
    ai_context = {
        "audit_context": {
            "duration_days": context["duration_days"],
            "audit_confidence": context["audit_confidence"],
            "warning": context["warning"],
        },
        "cashflow": cashflow,
        "spending_summary": {
            "essential_ratio": spending["spending_profile"]["essential_ratio"],
            "discretionary_ratio": spending["spending_profile"]["discretionary_ratio"],
            "top_categories": top_categories,
        },
        "risk_summary": {
            "duplicate_count": duplicate_count,
            "duplicate_vendors": duplicate_vendors,
            "subscription_count": subscription_count,
            "monthly_subscription_total": monthly_subscription_total,
            "subscription_vendors": subscription_vendors,
            "anomaly_count": anomaly_count,
            "largest_anomaly": largest_anomaly,
            "largest_anomaly_vendor": largest_anomaly_vendor,
            "top_anomalies": top_anomalies,
            "emi": risks["emi"],
        },
    }
    return ai_context

def generate_ai_audit(analytics):
    import os
    mock_audit = getattr(settings, "MOCK_AUDIT", True) or not getattr(settings, "GEMINI_API_KEY", None)

    if mock_audit:
        import time
        time.sleep(2.0)
        return {
            "risk_level": "MODERATE",
            "overall_summary": "Based on deterministic analytics, there are moderate risks detected in the statement, including some subscription costs and minor anomalies.",
            "strengths": [
                "Healthy savings rate.",
                "Essential category spending is within reasonable bounds."
            ],
            "concerns": [
                "Multiple duplicate charges detected (possible double billing).",
                "High discretionary spending in food and shopping categories."
            ],
            "suspicious_activity": [
                "Duplicate Swiggy charge.",
                "Unusual large transaction."
            ],
            "recommendations": [
                "Review the duplicate Swiggy transactions for a potential refund.",
                "Set a budget for discretionary spending categories.",
                "Audit the large transactions to confirm authorization."
            ],
            "final_verdict": "The statement shows a reasonable financial status with some opportunities for optimization."
        }

    ai_context = build_ai_context(analytics)
    prompt = build_audit_prompt(ai_context)

    provider = get_llm_provider(operation="ai_audit", statement_id=statement_id)

    try:
        result = provider.generate_content(
            prompt=prompt,
            schema=AIAuditSchema,
            temperature=0.0
        )
        return result
    except Exception as e:
        raise Exception(f"Failed to complete AI audit: {e}")