from google.adk.agents import LlmAgent
from config.email_config import PROCUREMENT_EMAIL, LEGAL_EMAIL, ADMIN_EMAIL

notification_agent = LlmAgent(
    name="NotificationAgent",
    model="gemini-2.5-flash",
    instruction=f"""
Send notifications.
LOW → {PROCUREMENT_EMAIL}
MEDIUM → {PROCUREMENT_EMAIL}, {LEGAL_EMAIL}
HIGH → {LEGAL_EMAIL}, {ADMIN_EMAIL}

Return JSON:
{{ "recipients": [], "subject": "", "body": "" }}
"""
)

