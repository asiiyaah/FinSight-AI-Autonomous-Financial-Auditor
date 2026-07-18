from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated

from chatbot.serializers import ChatRequestSerializer, ChatResponseSerializer
from chatbot.services import chat_with_statement


class StatementChatView(APIView):
    """
    API endpoint for interacting with the chatbot for a specific statement.
    Expects a POST request with a valid "message" in the body.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, statement_id: int):
        # 1. Validate the incoming request body
        request_serializer = ChatRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_message = request_serializer.validated_data["message"]

        # 2. Delegate the business logic to the service layer
        result = chat_with_statement(
            statement_id=statement_id,
            message=validated_message,
            user=request.user
        )

        # 3. Determine HTTP status code and format the response
        status_code = result.pop("status_code", status.HTTP_200_OK)
        response_serializer = ChatResponseSerializer(instance=result)

        return Response(response_serializer.data, status=status_code)
