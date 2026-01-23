from google.adk.agents import LlmAgent
from config.email_config import PROCUREMENT_EMAIL, LEGAL_EMAIL, ADMIN_EMAIL

# Enterprise sanctions list (can later be moved to config/policy)
SANCTIONED_COUNTRIES = {"IR", "KP", "SY", "CU", "RU"}

legal_review_agent = LlmAgent(
    name="LegalReviewAgent",
    model="gemini-2.5-flash",
    instruction=f"""
You are a Legal Review Agent in a supplier onboarding system.

IMPORTANT COMPLIANCE RULE:
- If the supplier is from a SANCTIONED COUNTRY (e.g. IR, KP, SY, CU, RU),
  then NO legal review should be conducted.
- In such cases, legal review must be marked as NOT_APPLICABLE.

Sanctioned country override:
- status = "NOT_APPLICABLE"
- review = "Legal review not applicable due to sanctions restrictions"

For non-sanctioned suppliers:
- Perform standard legal review checks
- If no issues are found:
    status = "COMPLETED"
    review = "No legal issues identified"

Return STRICT JSON only in the following format:
{{
  "status": "",
  "review": ""
}}
"""
)
