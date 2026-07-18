from typing import Tuple, Dict, Any
from chatbot.enums import Intent
from chatbot.constants import MERCHANTS, CATEGORIES, INTENT_RULES

def detect_intent(message: str) -> Tuple[Intent, Dict[str, Any]]:
    """
    Analyzes the user's message to determine the primary intent
    and extracts any relevant entities (e.g., merchant names, categories).
    Returns a tuple of (Intent, entities_dict).
    """
    msg_lower = message.lower()
    entities = {}
    
    # 1. Extract Entities (Preserving display names via dictionary values)
    for key, display_name in MERCHANTS.items():
        if key in msg_lower:
            entities["merchant"] = display_name
            break
            
    for key, display_name in CATEGORIES.items():
        if key in msg_lower:
            entities["category"] = display_name
            break
            
    # 2. Detect Intent via Rules mapping
    detected_intent = None
    for intent, keywords in INTENT_RULES.items():
        if any(word in msg_lower for word in keywords):
            detected_intent = intent
            break
            
    # 3. Handle Fallbacks and Special Cases
    if not detected_intent:
        detected_intent = Intent.SUMMARY

    # Crossover logic for spending questions
    if detected_intent in (Intent.TRANSACTION, Intent.CATEGORY):
        if "merchant" in entities:
            detected_intent = Intent.TRANSACTION
        elif "category" in entities:
            detected_intent = Intent.CATEGORY
            
    return detected_intent, entities
