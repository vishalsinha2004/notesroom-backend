# coursework/utils.py
import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

def send_brevo_email(to_email, subject, body):
    configuration = sib_api_v3_sdk.Configuration()
    # Use the same BREVO_SMTP_PASSWORD which is your API Key
    configuration.api_key['api-key'] = os.environ.get('BREVO_SMTP_PASSWORD')

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"email": os.environ.get('BREVO_SMTP_LOGIN'), "name": "Notesroom"},
        subject=subject,
        html_content=f"<html><body>{body}</body></html>"
    )

    try:
        api_instance.send_trans_email(send_smtp_email)
        return True
    except ApiException as e:
        print(f"Exception when calling Brevo API: {e}")
        return False