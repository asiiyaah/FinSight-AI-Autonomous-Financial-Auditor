from django.test import TestCase
import datetime
from financial_engine.detectors.anomalies import detect_anomalies

class AnomalyDetectorTests(TestCase):

    def test_anomaly_detection_rules(self):
        txs = [
            {"id": 1, "date": datetime.date(2024, 1, 1), "vendor": "HDFC BANK ATM", "normalized_vendor": "hdfc bank atm", "amount": 15000.0, "category": "Uncategorized", "transaction_type": "debit"},
            {"id": 2, "date": datetime.date(2024, 1, 2), "vendor": "LATE FEE CHARGE", "normalized_vendor": "late fee charge", "amount": 500.0, "category": "Uncategorized", "transaction_type": "debit"}
        ]
        anomalies = detect_anomalies(txs)
        self.assertEqual(len(anomalies), 2)
        types = [a["type"] for a in anomalies]
        self.assertIn("rule_atm", types)
        self.assertIn("rule_penalty", types)
        
        # Check standard metadata
        self.assertEqual(anomalies[0]["source"], "deterministic")
        self.assertIn("confidence", anomalies[0])
