from django.test import TestCase
from financial_engine.normalizer import normalize_vendor_name
from financial_engine.merchant_mapping import MERCHANT_CATEGORY_MAP

class NormalizationCategorizationTests(TestCase):

    def test_vendor_normalization(self):
        self.assertEqual(normalize_vendor_name("UPI/PAYTM/12345/Swiggy"), "swiggy")
        self.assertEqual(normalize_vendor_name("NETFLIX INC 12-05"), "netflix")
        self.assertEqual(normalize_vendor_name("HDFC BANK LOAN 2023"), "hdfc bank loan")
        self.assertEqual(normalize_vendor_name("POS/123/Starbucks"), "starbucks")

    def test_merchant_mapping(self):
        self.assertEqual(MERCHANT_CATEGORY_MAP.get("swiggy"), "Food Delivery")
        self.assertEqual(MERCHANT_CATEGORY_MAP.get("netflix"), "Subscription")
