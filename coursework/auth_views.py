import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import OTP, UserProfile 
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
        name = request.data.get('name', '')  # <--- 1. Grab the name from React
        
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user but mark as inactive until verified
        user = User.objects.create_user(username=email, email=email, password=password)
        
        # --- NEW: Save their real name! ---
        if name:
            user.first_name = name
        # ----------------------------------
        
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
            otp_record = OTP.objects.filter(user=user).last() 
            
            if otp_record and otp_record.code == otp_code:
                user.is_active = True
                user.save()
                otp_record.delete() 
                
                # --- NEW CODE: GENERATE TOKENS ---
                # Now that they are verified, log them in immediately!
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    "message": "Email verified successfully.",
                    "access": str(refresh.access_token),  # Send Access Token
                    "refresh": str(refresh)               # Send Refresh Token
                }, status=status.HTTP_200_OK)
                # ---------------------------------
                
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
        
        # Safely fetch the picture if the profile exists
        picture_url = None
        if hasattr(user, 'profile'):
            picture_url = user.profile.profile_picture

        # THE FIX: If the user has a first_name (from Google), use that! 
        # Otherwise, fall back to the username.
        display_name = user.first_name if user.first_name else user.username

        return Response({
            "username": display_name, # Send the beautiful display name!
            "email": user.email,
            "profile_picture": picture_url
        }, status=status.HTTP_200_OK)   
    
class GoogleLoginView(APIView):
    def post(self, request):
        print("DATA FROM REACT:", request.data) 
        
        token = request.data.get('token')
        if not token:
            print("ERROR: Token is missing!")
            return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            client_id = os.environ.get('GOOGLE_CLIENT_ID')
            print("DJANGO CLIENT ID IS:", client_id) 
            
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                client_id,
                clock_skew_in_seconds=10
            )
            
            # 2. Extract User Info from the Validated Token
            email = idinfo['email']
            name = idinfo.get('name', '')
            picture = idinfo.get('picture', '')
            
            # 3. Get or create the user (ONLY core fields in defaults)
            user, created = User.objects.get_or_create(email=email, defaults={
                'username': email,
            })
            
            # --- THE FIX IS HERE ---
            # Force update the user's name every time they log in
            # This fixes old accounts that were created before we added the name logic!
            if name:
                user.first_name = name
                
            # Make sure they are active
            if not user.is_active:
                user.is_active = True
                
            # Save the changes to the database!
            user.save()
            # -----------------------
            
            # Save the profile picture to our new table
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if picture:
                profile.profile_picture = picture
                profile.save()

            # 4. Generate your application's JWT tokens
            refresh = RefreshToken.for_user(user)
            
            print(f"SUCCESS! Logged in user: {email} with name {name}")
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'is_new_user': created,
                'message': 'Google authentication successful.'
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            print("GOOGLE REJECTED TOKEN BECAUSE:", str(e)) 
            return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print("SERVER ERROR:", str(e))
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)