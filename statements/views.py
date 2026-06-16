from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Statement
from .parser import parse_statement
from audits.audit_engine import run_full_audit
from .serializers import StatementListSerializer
from rest_framework.pagination import PageNumberPagination


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

        audit_context = statement.analytics.get("audit_context", {})

        response_data = {
            "statement": {
                "id": statement.id,
                "file_name": statement.file_name,
                "uploaded_at": statement.uploaded_at,
                "audit_status": statement.audit_status,
                "transaction_count": audit_context.get("transaction_count"),
                "duration_days": audit_context.get("duration_days"),
                "file_url": statement.file.url if statement.file else None,
            },
            "analytics": statement.analytics,
            "ai_audit": statement.ai_audit,
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
        status=status.HTTP_200_OK
    )


class StatementUploadView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        file=request.FILES.get('file')

        if not file:
            return Response({"error:FILE NOT PROVIDED"},status=status.HTTP_400_BAD_REQUEST)
        
        file_name=file.name
        if not file_name.endswith('.csv') and not file_name.endswith('.pdf'):
            return Response({"error": "Only CSV and PDF files are allowed"}, status=status.HTTP_400_BAD_REQUEST)
    
        file_type = 'csv' if file_name.endswith('.csv') else 'pdf'

        statement=Statement.objects.create(
            user=request.user,
            file=file,
            file_name=file_name,
            file_type=file_type,
        )
        count=parse_statement(statement)

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
            "file_type": statement.file_type,
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
                {"error": "Statement not parsed yet"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = run_full_audit(statement.id)

            return Response(
                {
                    "message": "Audit completed successfully",
                    "statement_id": statement.id,
                    "result": result
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "error" : str(e) ,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )