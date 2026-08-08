from rest_framework.views import APIView
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from rest_framework.permissions import IsAuthenticated
from .models import Statement
from .parser import parse_statement
from .pdf_generator import generate_audit_pdf
from audits.audit_engine import run_full_audit
from .serializers import StatementListSerializer
from rest_framework.pagination import PageNumberPagination
from services.llm.exceptions import LLMError


# Create your views here.

class StatementListView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request):
        
        statements=Statement.objects.filter(user=request.user).order_by("-uploaded_at")
        paginator = PageNumberPagination()
        paginated_statements = paginator.paginate_queryset(statements, request)
        serializer=StatementListSerializer(paginated_statements , many = True)
        
        return paginator.get_paginated_response(serializer.data)

class StatementDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, statement_id):
        try:
            statement = Statement.objects.get(
                id=statement_id,
                user=request.user
            )
        except Statement.DoesNotExist:
            return Response(
                {"error": "Statement not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Compute Layer A deterministic analytics if they don't exist yet
        if statement.is_parsed and (not statement.analytics or "audit_context" not in statement.analytics):
            from audits.audit_engine import run_audit
            try:
                statement.analytics = run_audit(statement.id)
                if statement.audit_status == "uploaded":
                    statement.audit_status = "analytics_ready"
                statement.save()
            except Exception as e:
                print(f"Error computing analytics on-the-fly: {e}")

        audit_context = statement.analytics.get("audit_context", {}) if statement.analytics else {}

        response_data = {
            "statement": {
                "id": statement.id,
                "file_name": statement.file_name,
                "uploaded_at": statement.uploaded_at,
                "audit_status": statement.audit_status,
                "transaction_count": audit_context.get("transaction_count", 0),
                "duration_days": audit_context.get("duration_days", 0),
                "file_url": f"/api/v1/statements/{statement.id}/file/" if statement.file else None,
            },
            "analytics": statement.analytics if statement.analytics else {},
            "ai_audit": statement.ai_audit if statement.ai_audit else {},
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def delete(self, request, statement_id):
        try:
            statement = Statement.objects.get(
                id=statement_id,
                user=request.user
            )
        except Statement.DoesNotExist:
            return Response(
                {"error": "Statement not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Delete uploaded file from media folder
        if statement.file:
            statement.file.delete(save=False)

        statement.delete()

        return Response(
            {"message": "Statement deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


class StatementFileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, statement_id):
        try:
            statement = Statement.objects.get(
                id=statement_id,
                user=request.user
            )
        except Statement.DoesNotExist:
            return Response(
                {"error": "Statement not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not statement.file:
            return Response(
                {"error": "File not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            return FileResponse(statement.file.open('rb'), content_type='application/pdf')
        except Exception:
            return Response(
                {"error": "File is missing from disk or unreadable"},
                status=status.HTTP_404_NOT_FOUND
            )

class StatementUploadView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        file=request.FILES.get('file')

        if not file:
            return Response({"success": False, "error_code": "NO_FILE", "message": "File not provided"},status=status.HTTP_400_BAD_REQUEST)
        
        file_name=file.name
        if not file_name.endswith('.pdf'):
            return Response({"success": False, "error_code": "INVALID_FORMAT", "message": "Only PDF files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

        # Temporary variable to track the statement so we can delete the file on failure
        temp_statement = None

        try:
            with transaction.atomic():
                statement = Statement.objects.create(
                    user=request.user,
                    file=file,
                    file_name=file_name,
                )
                temp_statement = statement
                
                count = parse_statement(statement)

                if count == 0:
                    raise ValueError("No transactions found in the parsed document.")

            # If we reach here, the transaction was committed successfully!
            return Response(
                {
                    "message": "Statement uploaded successfully",
                    "statement_id": statement.id,
                    "file_name": statement.file_name,
                    "uploaded_at": statement.uploaded_at,
                    "transactions_parsed": count,
                },status=status.HTTP_200_OK
            )

        except LLMError as e:
            if temp_statement and temp_statement.file:
                temp_statement.file.delete(save=False)
            return Response(
                {
                    "success": False,
                    "error_code": type(e).__name__,
                    "message": str(e)
                },
                status=status.HTTP_502_BAD_GATEWAY
            )
        except ValueError as e:
            if temp_statement and temp_statement.file:
                temp_statement.file.delete(save=False)
            return Response(
                {
                    "success": False,
                    "error_code": "PARSE_ERROR",
                    "message": str(e)
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except Exception as e:
            if temp_statement and temp_statement.file:
                temp_statement.file.delete(save=False)
            return Response(
                {
                    "success": False,
                    "error_code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred during upload."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class StatementAuditView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request,statement_id):

        try:
            statement=Statement.objects.get(
                id=statement_id,
                user=request.user
                )
            
        except Statement.DoesNotExist:
            return Response(
                {"error": "Statement not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not statement.is_parsed:
            return Response(
                {"error": "Statement not parsed yet. Please ensure the PDF was successfully uploaded and parsed before running the audit."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if statement.ai_audit:
            return Response(
                {
                    "message": "Audit already completed",
                    "statement_id": statement.id,
                    "analytics": statement.analytics,
                    "ai_audit": statement.ai_audit
                },
                status=status.HTTP_200_OK
            )

        try:
            result = run_full_audit(statement.id)

            return Response(
                {
                    "message": "Audit completed successfully",
                    "statement_id": statement.id,
                    "analytics": result.get("analytics", {}),
                    "ai_audit": result.get("ai_audit", {})
                },
                status=status.HTTP_200_OK
            )
        except LLMError as e:
            return Response(
                {
                    "success": False,
                    "error_code": type(e).__name__,
                    "error": str(e)
                },
                status=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error_code": "INTERNAL_ERROR",
                    "error": "Failed to complete audit",
                    "details": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StatementAuditDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, statement_id):
        try:
            statement = Statement.objects.get(id=statement_id, user=request.user)
        except Statement.DoesNotExist:
            return Response(
                {"error": "Statement not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not statement.ai_audit:
            return Response(
                {"error": "AI Audit data is missing or incomplete for this statement."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pdf_buffer = generate_audit_pdf(statement, statement.ai_audit)
            return FileResponse(
                pdf_buffer,
                as_attachment=True,
                filename=f"finsight_audit_{statement.id}.pdf",
                content_type="application/pdf"
            )
        except Exception as e:
            return Response(
                {"error": "Failed to generate PDF."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )