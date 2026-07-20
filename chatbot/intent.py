from typing import Tuple, Dict, Any, List
from chatbot.enums import Intent
from chatbot.constants import MERCHANTS, CATEGORIES, INTENT_RULES

def detect_intent(message: str, focus: Optional[Dict[str, Any]] = None) -> Tuple[List[Tuple[Intent, float]], Dict[str, Any]]:
    """
    Analyzes the user's message to determine the primary intents
    and extracts any relevant entities (e.g., merchant names, categories).
    Uses previous `focus` to resolve pronouns (e.g. "it", "one", "most expensive").
    Returns a tuple of (List of (Intent, Confidence), entities_dict).
    """
    msg_lower = message.lower()
    entities = {}
    
    # Check for pronoun references
    reference_words = ["it", "one", "those", "them", "first", "second", "last", "these"]
    has_reference = any(word in msg_lower.split() for word in reference_words)

    # If focus exists and pronoun used, inject the focus entities
    if has_reference and focus:
        if focus.get("type") == "intent":
            # If focus is just an intent type, we boost it
            pass
        elif focus.get("type") in ["category", "merchant"]:
            # If focus is a specific entity, inject it
            entities[focus["type"]] = focus.get("value")
    
    # 1. Extract Entities (Preserving display names via dictionary values)
    if "merchant" not in entities:
        for key, display_name in MERCHANTS.items():
            if key in msg_lower:
                entities["merchant"] = display_name
                break
                
    if "category" not in entities:
        for key, display_name in CATEGORIES.items():
            if key in msg_lower:
                entities["category"] = display_name
                break
                
    # 2. Score Intents via Rules mapping
    intent_scores = {}
    for intent, keywords in INTENT_RULES.items():
        match_count = sum(1 for word in keywords if word in msg_lower)
        if match_count > 0:
            # Simple heuristic score based on match count
            score = min(0.6 + (match_count * 0.15), 0.95)
            intent_scores[intent] = score
            
    # Boost based on focus if reference used
    if has_reference and focus and focus.get("intent_type"):
        focused_intent_str = focus.get("intent_type")
        for i in Intent:
            if i.value == focused_intent_str:
                intent_scores[i] = intent_scores.get(i, 0.7) + 0.3

    # Crossover logic for spending questions
    if "merchant" in entities:
        intent_scores[Intent.TRANSACTION] = intent_scores.get(Intent.TRANSACTION, 0.7) + 0.2
    if "category" in entities:
        intent_scores[Intent.CATEGORY] = intent_scores.get(Intent.CATEGORY, 0.7) + 0.2

    # 3. Handle Fallbacks and Normalize
    if not intent_scores:
        intent_scores[Intent.SUMMARY] = 0.85
        
    # Cap scores at 0.99
    for intent in intent_scores:
        intent_scores[intent] = min(intent_scores[intent], 0.99)
        
    # Sort by confidence descending
    sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
            
    return sorted_intents, entities
