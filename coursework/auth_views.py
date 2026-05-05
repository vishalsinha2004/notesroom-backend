# coursework/auth_views.py
import os
import random
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
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

        # 3. Send the email via Brevo API (NOT SMTP)
        configuration = sib_api_v3_sdk.Configuration()
        # Uses your BREVO_SMTP_PASSWORD which acts as your API Key
        configuration.api_key['api-key'] = os.environ.get('BREVO_SMTP_PASSWORD')

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email}],
            sender={"email": os.environ.get('BREVO_SMTP_LOGIN'), "name": "Notesroom"},
            subject="Your Notesroom Verification Code",
            html_content=f"""
                <html>
                    <body style="font-family: sans-serif; padding: 20px;">
                        <h2 style="color: #2563eb;">Welcome to Notesroom!</h2>
                        <p>Your verification code is: <strong style="font-size: 24px;">{code}</strong></p>
                        <p>This code will expire in 10 minutes.</p>
                    </body>
                </html>
            """
        )

        try:
            api_instance.send_transac_email(send_smtp_email)
            return Response({"message": "Verification code sent.", "email": email}, status=status.HTTP_201_CREATED)
        except ApiException as e:
            # If email fails, we should still return the response but maybe log the error
            print(f"Brevo API Error: {e}")
            return Response({"message": "User created, but failed to send email. Check API key."}, status=status.HTTP_201_CREATED)

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        try:
            user = User.objects.get(email=email)
            otp = OTP.objects.get(user=user)
            
            if otp.code == code and otp.is_valid():
                user.is_active = True
                user.save()
                otp.delete() 
                return Response({"message": "Email verified successfully!"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired verification code."}, status=status.HTTP_400_BAD_REQUEST)
                
        except (User.DoesNotExist, OTP.DoesNotExist):
            return Response({"error": "User or verification code not found."}, status=status.HTTP_400_BAD_REQUEST)