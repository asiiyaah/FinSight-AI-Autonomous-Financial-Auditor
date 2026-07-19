# Centralized configuration and tuning parameters for the Financial Intelligence Engine

# Dynamic Confidence Weights for Detectors
CONFIDENCE_WEIGHTS = {
    "category_match": 0.50,
    "keyword_match": 0.45,
    "recurring_enrichment": 0.25,
}

# Detection Thresholds
THRESHOLDS = {
    "subscription_min_confidence": 0.40,
    "emi_min_confidence": 0.45,
}
