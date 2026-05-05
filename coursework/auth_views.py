# coursework/auth_views.py
import random
from django.contrib.auth.models import User
from django.core.mail import send_mail
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

        # 3. Send the email via Brevo
        send_mail(
            subject='Your Notesroom Verification Code',
            message=f'Your verification code is: {code}\n\nThis code will expire in 10 minutes.',
            from_email=None, 
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "Verification code sent.", "email": email}, status=status.HTTP_201_CREATED)

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        try:
            user = User.objects.get(email=email)
            otp = OTP.objects.get(user=user)
            
            # Check if code matches and is not expired
            if otp.code == code and otp.is_valid():
                user.is_active = True
                user.save()
                otp.delete() # Delete the code after it's used successfully
                return Response({"message": "Email verified successfully!"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired verification code."}, status=status.HTTP_400_BAD_REQUEST)
                
        except (User.DoesNotExist, OTP.DoesNotExist):
            return Response({"error": "User or verification code not found."}, status=status.HTTP_400_BAD_REQUEST)