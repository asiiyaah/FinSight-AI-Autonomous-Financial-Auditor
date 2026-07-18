from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    """
    Validates incoming chat requests.
    Ensures the message is provided, is a valid string, and does not exceed length limits.
    """
    message = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=1000,
        error_messages={
            "required": "A message is required to chat.",
            "blank": "The message cannot be empty.",
            "max_length": "The message cannot exceed 1000 characters."
        }
    )

    def validate_message(self, value: str) -> str:
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "The message cannot be empty."
            )

        return value


class ChatResponseSerializer(serializers.Serializer):
    """
    Formats the outgoing chat responses from the backend engine.
    Used for API documentation and response generation.
    """
    success = serializers.BooleanField(read_only=True)
    answer = serializers.CharField(required=False, allow_blank=True, allow_null=True, read_only=True)
    intent = serializers.CharField(required=False, allow_blank=True, allow_null=True, read_only=True)
    message = serializers.CharField(required=False, allow_blank=True, allow_null=True, read_only=True)
