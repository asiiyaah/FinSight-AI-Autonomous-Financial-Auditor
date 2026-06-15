from typing import Dict,Any


def get_top_categories(category_breakdown,top_n=3):

        sorted_categories = sorted(
        category_breakdown.items(),
        key=lambda item: item[1],
        reverse=True
    )
        
        return sorted_categories[:top_n]


def build_ai_context(analytics : Dict[str,Any]):

    context = analytics["audit_context"]
    cashflow = analytics["cashflow"]
    spending = analytics["spending"]
    risks = analytics["risks"]

    category_breakdown = spending["category_breakdown"]
    top_categories = get_top_categories(category_breakdown)

    duplicate_vendors = []

    duplicate_count = len(risks["duplicates"])
    for group in risks["duplicates"]:
          if group:
                duplicate_vendors.append(group[0]["vendor"])

    subscription_count = len(risks["subscriptions"])

    monthly_subscription_total = sum(
          sub["amount"] for sub in risks["subscriptions"]
    )

    subscription_vendors = [
        sub["vendor"] for sub in risks["subscriptions"]
    ]

    anomaly_count = len(risks["anomalies"])

    largest_anomaly = None
    largest_anomaly_vendor = None
    top_anomalies = []

    if anomaly_count > 0 :
          largest = max(
                risks["anomalies"],
                key = lambda x :x["amount"],
          )
          
    largest_anomaly = largest['amount']
    largest_anomaly_vendor = largest['vendor']

    sorted_anomalies = sorted(
          risks["anomalies"],
          key = lambda x : x["amount"],  
          reverse=True
    )

    top_anomalies = sorted_anomalies[:3]


    ai_context = {
        "audit_context": {
            "duration_days": context["duration_days"],
            "audit_confidence": context["audit_confidence"],
            "warning": context["warning"]
        },

        "cashflow": cashflow,

        "spending_summary": {
            "essential_ratio": spending["spending_profile"]["essential_ratio"],
            "discretionary_ratio": spending["spending_profile"]["discretionary_ratio"],
            "top_categories": top_categories
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

            "emi": risks["emi"]
        }
    }