from rest_framework import serializers
from .models import Statement

class StatementListSerializer(serializers.ModelSerializer):
    transaction_count = serializers.SerializerMethodField()

    class Meta:
        model = Statement
        fields = ['id', 'file_name', 'uploaded_at', 'audit_status', 'transaction_count']

    def get_transaction_count(self, obj):
        return obj.transactions.count()