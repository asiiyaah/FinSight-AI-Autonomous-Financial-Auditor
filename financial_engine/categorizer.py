import time
from typing import List, Dict, Set
from services.llm import get_llm_provider
from django.conf import settings
from pydantic import BaseModel
from statements.models import MerchantCategory
from .merchant_mapping import MERCHANT_CATEGORY_MAP

class MerchantCategoryResult(BaseModel):
    vendor: str
    category: str

class BatchCategorizationResponse(BaseModel):
    categorizations: list[MerchantCategoryResult]

def get_category_for_vendor(normalized_vendor: str) -> Dict[str, str]:
    """
    Get category for a single vendor. 
    First checks deterministic map, then DB cache, then AI fallback.
    Returns dict with keys: 'category', 'source', 'confidence'.
    """
    if normalized_vendor in MERCHANT_CATEGORY_MAP:
        return {
            "category": MERCHANT_CATEGORY_MAP[normalized_vendor],
            "source": "deterministic",
            "confidence": 1.0
        }
        
    try:
        cached = MerchantCategory.objects.get(normalized_vendor=normalized_vendor)
        return {
            "category": cached.category,
            "source": cached.source,
            "confidence": cached.confidence
        }
    except MerchantCategory.DoesNotExist:
        # We need AI fallback
        result = _ai_categorize_vendors([normalized_vendor])
        if result and normalized_vendor in result:
            cat = result[normalized_vendor]
            MerchantCategory.objects.create(
                normalized_vendor=normalized_vendor,
                category=cat,
                confidence=0.8,
                source='ai'
            )
            return {
                "category": cat,
                "source": "ai",
                "confidence": 0.8
            }
            
    return {
        "category": "Uncategorized",
        "source": "deterministic",
        "confidence": 0.0
    }

def batch_categorize_vendors(normalized_vendors: List[str]) -> Dict[str, Dict[str, str]]:
    """
    Categorize a list of vendors efficiently.
    """
    results = {}
    unknown_vendors = []
    
    # 1. Check deterministic map
    for vendor in normalized_vendors:
        if vendor in MERCHANT_CATEGORY_MAP:
            results[vendor] = {
                "category": MERCHANT_CATEGORY_MAP[vendor],
                "source": "deterministic",
                "confidence": 1.0
            }
        else:
            unknown_vendors.append(vendor)
            
    if not unknown_vendors:
        return results
        
    # 2. Check DB Cache
    cached_records = MerchantCategory.objects.filter(normalized_vendor__in=unknown_vendors)
    cached_map = {record.normalized_vendor: record for record in cached_records}
    
    vendors_to_ai = []
    for vendor in unknown_vendors:
        if vendor in cached_map:
            results[vendor] = {
                "category": cached_map[vendor].category,
                "source": cached_map[vendor].source,
                "confidence": cached_map[vendor].confidence
            }
        else:
            vendors_to_ai.append(vendor)
            
    if not vendors_to_ai:
        return results
        
    # 3. AI Fallback for remaining unknown vendors
    ai_results = _ai_categorize_vendors(vendors_to_ai)
    
    for vendor in vendors_to_ai:
        cat = ai_results.get(vendor, "Uncategorized")
        conf = 0.8 if cat != "Uncategorized" else 0.0
        
        # Save to DB cache
        MerchantCategory.objects.get_or_create(
            normalized_vendor=vendor,
            defaults={
                "category": cat,
                "confidence": conf,
                "source": "ai"
            }
        )
        
        results[vendor] = {
            "category": cat,
            "source": "ai",
            "confidence": conf
        }
        
    return results

def _ai_categorize_vendors(vendors: List[str]) -> Dict[str, str]:
    mock_parser = getattr(settings, "MOCK_PARSER", True) or not getattr(settings, "GEMINI_API_KEY", None)
    if mock_parser:
        return {vendor: "Other" for vendor in vendors}
        
    provider = get_llm_provider(operation="ai_categorization")
    
    prompt = f"""
    Categorize the following list of Indian merchant/vendor names into one of these categories:
    Food Delivery, Dining, Groceries, Utilities, Shopping, Subscription, Entertainment, Transport, Travel, EMI, Credit Card Bill, Healthcare, Income, Other.
    
    Vendors:
    {', '.join(vendors)}
    """
    
    try:
        result = provider.generate_content(
            prompt=prompt,
            schema=BatchCategorizationResponse
        )
        
        if result and "categorizations" in result:
            return {item["vendor"]: item["category"] for item in result["categorizations"]}
    except Exception as e:
        print(f"Failed AI categorization: {e}")
        
    return {vendor: "Other" for vendor in vendors}
