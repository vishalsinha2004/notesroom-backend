import requests
import threading
from django.conf import settings
from django.contrib.auth.models import User

# --- EXISTING OTP FEATURE ---
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


# --- NEW FEATURE: NEW DOCUMENT NOTIFICATION ---
def _send_bulk_email_task(document_title, subject_name, semester_name):
    # 1. Get all active user emails
    users = User.objects.filter(is_active=True).exclude(email='')
    bcc_list = [{"email": user.email} for user in users]

    # If no users exist yet, exit the function
    if not bcc_list:
        return

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json"
    }

    payload = {
        "sender": {
            "name": "NotesRoom", 
            "email": "notesroomofficial@gmail.com"
        }, 
        # Send the main email to yourself (dummy target), hide everyone else in BCC
        "to": [{"email": "notesroomofficial@gmail.com"}], 
        "bcc": bcc_list,
        "subject": f"📚 New Study Material: {document_title}",
        "htmlContent": f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 500px; margin: auto; padding: 30px; border: 1px solid #e2e8f0; border-radius: 16px; background-color: #ffffff;">
            <div style="text-align: center; margin-bottom: 20px;">
                <span style="font-size: 40px;">🎓</span>
            </div>
            <h2 style="color: #1e40af; text-align: center; margin-top: 0;">New Material Added!</h2>
            <p style="color: #334155; font-size: 16px;">Hello Student,</p>
            <p style="color: #334155; font-size: 16px;">A new document has just been uploaded to your Notesroom.</p>
            
            <div style="background-color: #f8fafc; padding: 20px; border-radius: 12px; margin: 25px 0; border-left: 4px solid #3b82f6;">
                <p style="margin: 8px 0; color: #0f172a; font-size: 15px;"><strong>📁 Semester:</strong> {semester_name}</p>
                <p style="margin: 8px 0; color: #0f172a; font-size: 15px;"><strong>📚 Subject:</strong> {subject_name}</p>
                <p style="margin: 8px 0; color: #0f172a; font-size: 15px;"><strong>📄 Title:</strong> {document_title}</p>
            </div>
            
            <p style="color: #334155; font-size: 16px;">Log in to Notesroom to read it or ask the AI Tutor questions about it!</p>
            <br>
            <p style="font-size: 14px; color: #64748b; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 20px;">
                Happy Studying,<br><strong>Notesroom Team</strong>
            </p>
        </div>
        """
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code not in [200, 201]:
            print(f"Brevo API Error (Bulk Email): {response.text}")
    except Exception as e:
        print(f"Error sending bulk email: {e}")

def send_new_document_notification(document):
    """
    We run this in a background thread. If we don't do this, clicking "Save" 
    in the Django Admin panel will freeze until all emails are sent!
    """
    thread = threading.Thread(
        target=_send_bulk_email_task, 
        args=(document.title, document.subject.name, document.subject.semester.name)
    )
    thread.start()