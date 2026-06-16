from rest_framework import serializers
from .models import Statement

class StatementListSerializer(serializers.ModelSerializer):
    class Meta:
        model=Statement
        fields=['id','file_name','uploaded_at','audit_status']
        