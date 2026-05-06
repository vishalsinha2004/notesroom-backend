import random
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import OTP

class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Create the user, set inactive
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False 
        user.save()

        # 2. Generate a 6-digit code and save it
        code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, code=code)
        
        # 3. NO EMAIL API: Print the code directly to the terminal for testing
        print("\n" + "="*50)
        print(f"🚨 NEW USER REGISTRATION: {email}")
        print(f"🔑 VERIFICATION CODE: {code}")
        print("="*50 + "\n")

        return Response({
            "message": "User created. Code printed to terminal for testing.", 
            "email": email
        }, status=status.HTTP_201_CREATED)