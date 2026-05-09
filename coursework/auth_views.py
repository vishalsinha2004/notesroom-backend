import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import OTP 
from .utils import send_otp_via_brevo

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