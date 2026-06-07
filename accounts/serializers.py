from rest_framework import serializers
from django.contrib.auth import get_user_model

#grabs CustomUser model linked in settings.py
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
  
    # API will NEVER return that password back in any JSON responses for safety.
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password','first_name', 'last_name']
   

# overrides Django's default save button
    def create(self, validated_data):
         
        # By using create_user it triggers Django's secure hashing to safely encrypt the password   
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        return user
