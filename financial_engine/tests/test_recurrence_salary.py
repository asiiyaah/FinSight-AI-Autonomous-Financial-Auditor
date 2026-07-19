from django.test import TestCase
import datetime
from financial_engine.detectors.recurring import detect_recurring_patterns
from financial_engine.detectors.salary import detect_salary

class RecurrenceSalaryTests(TestCase):

    def test_recurring_detector(self):
        txs = [
            {"date": datetime.date(2024, 1, 5), "vendor": "Netflix", "normalized_vendor": "netflix", "amount": 499.0, "category": "Subscription", "transaction_type": "debit"},
            {"date": datetime.date(2024, 2, 5), "vendor": "Netflix Inc", "normalized_vendor": "netflix", "amount": 499.0, "category": "Subscription", "transaction_type": "debit"},
            {"date": datetime.date(2024, 3, 5), "vendor": "Netflix", "normalized_vendor": "netflix", "amount": 499.0, "category": "Subscription", "transaction_type": "debit"},
        ]
        
        recurring = detect_recurring_patterns(txs, min_occurrences=2)
        self.assertEqual(len(recurring), 1)
        self.assertEqual(recurring[0]["vendor"], "netflix")
        self.assertEqual(recurring[0]["months_detected"], 3)
        self.assertEqual(recurring[0]["source"], "deterministic")

    def test_salary_detector(self):
        txs = [
            {"date": datetime.date(2024, 1, 1), "vendor": "Acme Corp Salary", "original_vendor": "Acme Corp Salary", "normalized_vendor": "acme corp", "amount": 50000.0, "category": "Income", "transaction_type": "credit"},
            {"date": datetime.date(2024, 2, 1), "vendor": "Acme Corp Salary", "original_vendor": "Acme Corp Salary", "normalized_vendor": "acme corp", "amount": 50000.0, "category": "Income", "transaction_type": "credit"},
        ]
        
        salary_info = detect_salary(txs)
        self.assertTrue(salary_info["detected"])
        self.assertEqual(salary_info["total_monthly_salary"], 50000.0)
        self.assertEqual(salary_info["sources"][0]["source"], "deterministic")
