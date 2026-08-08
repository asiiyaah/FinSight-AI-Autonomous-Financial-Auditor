from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from services.llm.exceptions import LLMRateLimitError, LLMProviderError
from statements.models import Statement


class StatementAIErrorHandlingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_upload_returns_safe_error_when_ai_service_fails(self):
        file_obj = SimpleUploadedFile(
            "statement.pdf",
            b"%PDF-1.4 sample content",
            content_type="application/pdf"
        )

        with patch("statements.views.parse_statement", side_effect=LLMRateLimitError()):
            response = self.client.post(
                "/api/v1/statements/upload/",
                {"file": file_obj},
                format="multipart"
            )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data["error_code"], "LLMRateLimitError")
        self.assertIn("Please try again", response.data["message"])
        self.assertEqual(Statement.objects.count(), 0)

    def test_run_ai_audit_returns_safe_error_and_preserves_statement_state(self):
        file_obj = SimpleUploadedFile(
            "statement.pdf",
            b"%PDF-1.4 sample content",
            content_type="application/pdf"
        )

        statement = Statement.objects.create(
            user=self.user,
            file=file_obj,
            file_name="statement.pdf",
            is_parsed=True,
            audit_status="analytics_ready",
            analytics={"audit_context": {"transaction_count": 1, "duration_days": 30, "audit_confidence": "medium", "warning": None}}
        )

        with patch("statements.views.run_full_audit", side_effect=LLMProviderError()):
            response = self.client.post(f"/api/v1/statements/{statement.id}/audit/")

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.data["error_code"], "LLMProviderError")
        self.assertIn("temporarily unavailable", response.data["error"].lower())

        statement.refresh_from_db()
        self.assertEqual(statement.audit_status, "analytics_ready")
        self.assertEqual(statement.ai_audit, {})
