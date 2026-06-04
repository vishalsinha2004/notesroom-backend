import requests
import threading
from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection


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


# --- UPDATED FEATURE: BULK EMAIL NOW SHOWS UPLOADER USERNAME ---
# Added 'uploader_username' to the parameters
def _send_bulk_email_task(document_title, subject_name, semester_name, uploader_username):
    try:  
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
                <p style="color: #334155; font-size: 16px;"><strong>{uploader_username}</strong> just uploaded a new document to your Notesroom.</p>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 12px; margin: 25px 0; border-left: 4px solid #3b82f6;">
                    <p style="margin: 8px 0; color: #0f172a; font-size: 15px;"><strong>📁 Semester:</strong> {semester_name}</p>
                    <p style="margin: 8px 0; color: #0f172a; font-size: 15px;"><strong>📚 Subject:</strong> {subject_name}</p>
                    <p style="margin: 8px 0; color: #0f172a; font-size: 15px;"><strong>📄 Title:</strong> {document_title}</p>
                    <p style="margin: 8px 0; color: #0f172a; font-size: 15px;"><strong>👤 Uploaded By:</strong> {uploader_username}</p>
                </div>
                
                <p style="color: #334155; font-size: 16px;">Log in to Notesroom to read it or ask the AI Tutor questions about it!</p>
                <br>
                <p style="font-size: 14px; color: #64748b; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 20px;">
                    Happy Studying,<br><strong>Notesroom Team</strong>
                </p>
            </div>
            """
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code not in [200, 201]:
            print(f"Brevo API Error (Bulk Email): {response.text}")
            
    except Exception as e:
        print(f"Error sending bulk email: {e}")
        
    finally:
        # Prevents PostgreSQL crash
        connection.close()


def send_new_document_notification(document):
    """
    We run this in a background thread. If we don't do this, clicking "Save" 
    in the Django Admin panel will freeze until all emails are sent!
    """
    # 1. Fetch the user safely (Fallback to email if username is somehow blank)
    if document.owner:
        uploader_name = document.owner.username or document.owner.first_name or document.owner.email or "A Student"
    else:
        uploader_name = "Notesroom Admin"
    
    # 2. Pass the username to the email thread
    thread = threading.Thread(
        target=_send_bulk_email_task, 
        args=(document.title, document.subject.name, document.subject.semester.name, uploader_name)
    )
    thread.start()


# --- FEATURE: ADMIN NOTIFICATION FOR STUDENT UPLOADS ---
def _send_admin_upload_notification_task(document_title, subject_name, semester_name, uploader_username):
    try:
        # 1. Get all admin emails (superusers)
        admin_emails = list(User.objects.filter(is_superuser=True).values_list('email', flat=True))
        
        # If no superuser emails exist, fall back to the main official email
        if not admin_emails:
            admin_emails = ['notesroomofficial@gmail.com']

        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json"
        }

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #2563eb;">New Document Uploaded by Student</h2>
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px;">
                    <p><strong>Student Name:</strong> {uploader_username}</p>
                    <p><strong>Document Title:</strong> {document_title}</p>
                    <p><strong>Location:</strong> {semester_name} &gt; {subject_name}</p>
                </div>
                <br>
                <p>Please log in to the Django Admin panel to review this document.</p>
            </body>
        </html>
        """

        # Send individual emails to all admins
        for admin_email in admin_emails:
            if not admin_email: 
                continue
                
            payload = {
                "sender": {
                    "name": "NotesRoom System", 
                    "email": "notesroomofficial@gmail.com"
                },
                "to": [{"email": admin_email}],
                "subject": f"New Upload Alert: {document_title} from {uploader_username}",
                "htmlContent": html_content
            }
            
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code not in [200, 201]:
                print(f"Brevo API Error (Admin Alert): {response.text}")

    except Exception as e:
        print(f"Error sending admin upload notification: {e}")
        
    finally:
        connection.close()


def send_admin_upload_notification(document):
    """
    Called when a student uploads a document via the frontend.
    Runs in a thread so the frontend UI doesn't freeze while waiting for Brevo.
    """
    uploader_username = document.owner.username if document.owner else "Unknown Student"
    
    thread = threading.Thread(
        target=_send_admin_upload_notification_task,
        args=(document.title, document.subject.name, document.subject.semester.name, uploader_username)
    )
    thread.start()