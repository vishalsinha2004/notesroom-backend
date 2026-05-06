import requests
from django.conf import settings

def send_otp_via_brevo(email, otp_code):
    url = "https://api.brevo.com/v3/smtp/email"
    
    payload = {
        "sender": {
            "name": "NotesRoom", 
            "email": "notesroomofficial@gmail.com" # IMPORTANT: Must be a sender email verified in your Brevo account
        },
        "to": [
            {
                "email": email
            }
        ],
        "subject": "Your NotesRoom Verification Code",
        "htmlContent": f"""
            <html>
                <body>
                    <h3>Welcome to NotesRoom!</h3>
                    <p>Your OTP for email verification is: <strong style="font-size: 20px;">{otp_code}</strong></p>
                    <p>Please enter this code to activate your account.</p>
                </body>
            </html>
        """
    }
    
    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code in [200, 201]:
        return True
    else:
        print(f"Brevo API Error: {response.text}")
        return False