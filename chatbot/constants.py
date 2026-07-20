from chatbot.enums import Intent

MERCHANTS = {
    "amazon": "Amazon",
    "amazon shopping": "Amazon",
    "amazon pay": "Amazon",
    "swiggy": "Swiggy",
    "zomato": "Zomato",
    "flipkart": "Flipkart",
    "uber": "Uber",
    "ola": "Ola",
    "blinkit": "Blinkit",
    "cred": "CRED",
    "phonepe": "PhonePe",
    "phone pe": "PhonePe",
    "phonepe p2m": "PhonePe",
    "phonepe upi": "PhonePe",
    "gpay": "GPay",
    "google pay": "GPay",
    "hdfc": "HDFC",
    "netflix": "Netflix",
}

CATEGORIES = {
    "food": "Food",
    "dining": "Food",
    "shopping": "Shopping",
    "travel": "Transport",
    "transport": "Transport",
    "fuel": "Fuel",
    "medical": "Healthcare",
    "health": "Healthcare",
    "groceries": "Groceries",
    "entertainment": "Entertainment",
}

INTENT_RULES = {
    Intent.RECOMMENDATION: ["recommend", "advice", "improve"],
    Intent.ANOMALY: ["anomaly", "unusual", "duplicate", "double"],
    Intent.SUBSCRIPTION: ["subscription", "recurring", "netflix"],
    Intent.EMI: ["emi", "loan"],
    Intent.CASHFLOW: ["cashflow", "balance", "save", "saving", "salary", "income", "payroll", "deposit"],
    Intent.TOP_SPENDING: ["top", "highest", "biggest", "expensive", "most", "largest"],
    Intent.SUMMARY: ["summary", "summarize", "overall"],
    Intent.CATEGORY: ["category", "breakdown", "food", "travel", "shopping"],
    Intent.TRANSACTION: ["transaction", "spend", "spent", "purchase", "purchases", "amazon", "swiggy", "zomato", "withdrawal", "withdrawals"],
}
