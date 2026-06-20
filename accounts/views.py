from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from .serializers import RegisterSerializer  , EmailLoginSerializer
from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken


def signup_page(request):
    return render(request, 'signup.html')


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
       
        serializer = RegisterSerializer(data=request.data)       
        
        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "User registered successfully!",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        user=request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        })

class EmailLoginView(APIView):
    permission_classes=[]

    def post(self,request):
        serializer=EmailLoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data)

    
    
