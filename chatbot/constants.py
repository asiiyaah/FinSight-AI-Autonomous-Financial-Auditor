from chatbot.enums import Intent

MERCHANTS = {
    "amazon": "Amazon",
    "swiggy": "Swiggy",
    "zomato": "Zomato",
    "flipkart": "Flipkart",
    "uber": "Uber",
    "ola": "Ola",
    "blinkit": "Blinkit",
    "cred": "CRED",
    "phonepe": "PhonePe",
    "hdfc": "HDFC",
    "netflix": "Netflix",
}

CATEGORIES = {
    "food": "Food & Dining",
    "dining": "Food & Dining",
    "shopping": "Shopping",
    "travel": "Travel",
    "fuel": "Fuel",
    "medical": "Medical",
}

INTENT_RULES = {
    Intent.RECOMMENDATION: ["recommend", "advice", "improve"],
    Intent.ANOMALY: ["anomaly", "unusual"],
    Intent.SUBSCRIPTION: ["subscription", "recurring", "netflix"],
    Intent.EMI: ["emi", "loan"],
    Intent.CASHFLOW: ["cashflow", "balance", "save", "saving"],
    Intent.TOP_SPENDING: ["top", "highest", "biggest", "expensive", "most"],
    Intent.SUMMARY: ["summary", "summarize", "overall"],
    Intent.CATEGORY: ["category", "breakdown", "food", "travel", "shopping"],
    Intent.TRANSACTION: ["transaction", "spend", "spent", "purchase", "purchases", "amazon", "swiggy", "zomato"],
}
