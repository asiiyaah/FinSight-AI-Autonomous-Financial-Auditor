from enum import Enum

class Intent(str, Enum):
    SUMMARY = "summary"
    CASHFLOW = "cashflow"
    CATEGORY = "category"
    SUBSCRIPTION = "subscription"
    EMI = "emi"
    ANOMALY = "anomaly"
    RECOMMENDATION = "recommendation"
    TRANSACTION = "transaction"
    SPENDING_ANALYSIS = "spending_analysis"
    TOP_SPENDING = "top_spending"
