from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Statement
from .parser import parse_statement
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
                "file_url": statement.file.url if statement.file else None,
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


class StatementUploadView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        file=request.FILES.get('file')

        if not file:
            return Response({"error": "FILE NOT PROVIDED"},status=status.HTTP_400_BAD_REQUEST)
        
        file_name=file.name
        if not file_name.endswith('.pdf'):
            return Response({"error": "Only PDF files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

        statement=Statement.objects.create(
            user=request.user,
            file=file,
            file_name=file_name,
        )
        
        try:
            count=parse_statement(statement)
        except LLMError as e:
            statement.audit_status = "failed"
            statement.save()
            # Delete partial transactions just in case
            statement.transactions.all().delete()
            return Response(
                {
                    "success": False,
                    "error_code": type(e).__name__,
                    "error": str(e)
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

#DESTRUCTION OF UNPARSED DOCUMENTS
        # =========================================================
        if count == 0:
            statement.delete()  
            return Response(
                {
                    "error": "Failed to parse transactions",
                    "message": "Upload aborted to prevent database pollution. Verify the file format or try again."
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        return Response(
            {
            "message": "Statement uploaded successfully",
            "statement_id": statement.id,
            "file_name": statement.file_name,
            "uploaded_at": statement.uploaded_at,
            "transactions_parsed": count,
            },status=status.HTTP_200_OK
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