import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import OTP 
from .utils import send_otp_via_brevo
from rest_framework.permissions import IsAuthenticated
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework_simplejwt.tokens import RefreshToken
import os

class RegisterView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user but mark as inactive until verified
        user = User.objects.create_user(username=email, email=email, password=password)
        user.is_active = False 
        user.save()
        
        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, code=otp_code)
        
        # Send via Brevo API
        email_sent = send_otp_via_brevo(email, otp_code)
        
        if email_sent:
            return Response({"message": "Registration successful. OTP sent to email."}, status=status.HTTP_201_CREATED)
        else:
            user.delete() # Rollback if email fails
            return Response({"error": "Failed to send OTP email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp')
        
        try:
            user = User.objects.get(email=email)
            # Get the most recently generated OTP for this user
            otp_record = OTP.objects.filter(user=user).last() 
            
            if otp_record and otp_record.code == otp_code:
                user.is_active = True
                user.save()
                otp_record.delete() # Clean up OTP after successful use
                return Response({"message": "Email verified successfully. You can now login."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
                
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

# --- NEW VIEW FOR RESENDING OTP ---
class ResendOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # If the user is already active, they don't need a new OTP
            if user.is_active:
                return Response({"error": "User is already verified."}, status=status.HTTP_400_BAD_REQUEST)
                
            # Clear any existing OTPs for this user
            OTP.objects.filter(user=user).delete()
            
            # Generate new 6-digit OTP
            otp_code = str(random.randint(100000, 999999))
            OTP.objects.create(user=user, code=otp_code)
            
            # Send via Brevo API
            email_sent = send_otp_via_brevo(email, otp_code)
            
            if email_sent:
                return Response({"message": "New OTP sent to email."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to send OTP email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
        }, status=status.HTTP_200_OK)
    
class GoogleLoginView(APIView):
    def post(self, request):
        # 1. Print the data React sent us (Great for debugging!)
        print("DATA FROM REACT:", request.data) 
        
        token = request.data.get('token')
        if not token:
            print("ERROR: Token is missing!")
            return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            client_id = os.environ.get('GOOGLE_CLIENT_ID')
            print("DJANGO CLIENT ID IS:", client_id) 
            
            # --- THE MAGIC FIX IS HERE ---
            # Added clock_skew_in_seconds=10 to forgive slight computer clock delays
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                client_id,
                clock_skew_in_seconds=10
            )
            
            # 2. Extract User Info from the Validated Token
            email = idinfo['email']
            name = idinfo.get('name', '')
            
            # 3. Get or create the user in your database
            user, created = User.objects.get_or_create(email=email, defaults={
                'username': email,
                'is_active': True # Google users are pre-verified
            })
            
            # If a user registered manually but never verified their OTP, activate them now
            if not user.is_active:
                user.is_active = True
                user.save()
            
            # 4. Generate your application's JWT tokens
            refresh = RefreshToken.for_user(user)
            
            print(f"SUCCESS! Logged in user: {email}")
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'is_new_user': created,
                'message': 'Google authentication successful.'
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            # 5. Print the EXACT reason Google rejected it
            print("GOOGLE REJECTED TOKEN BECAUSE:", str(e)) 
            return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print("SERVER ERROR:", str(e))
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)