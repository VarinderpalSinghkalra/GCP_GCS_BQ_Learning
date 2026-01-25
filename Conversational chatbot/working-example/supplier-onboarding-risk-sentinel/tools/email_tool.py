import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(recipients, subject, body):
    if not recipients:
        print("ℹ️ No recipients. Skipping email.")
        return False

    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key:
        print("❌ Missing SENDGRID_API_KEY")
        return False

    message = Mail(
        from_email="varinderpalsinghcareer@gmail.com",  # must be verified in SendGrid
        to_emails=recipients,
        subject=subject,
        plain_text_content=body,
    )

    try:
        SendGridAPIClient(api_key).send(message)
        print(f"✅ Email sent to {recipients}")
        return True
    except Exception as e:
        print("❌ SendGrid email failed:", str(e))
        return False
