from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Statement
from .parser import parse_statement
from audits.audit_engine import run_full_audit

# Create your views here.
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