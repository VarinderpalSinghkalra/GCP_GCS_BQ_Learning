import uuid
import logging
from flask import jsonify, Request

# -------------------------------------------------
# Logging
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# Gen-2 Cloud Function Entry Point
# -------------------------------------------------
def createIssue(request: Request):
"""
Gen-2 Cloud Function entry point for issue creation.
Compatible with Vertex AI Conversational Agents tools.
"""

try:
# Parse JSON safely
data = request.get_json(silent=True)
if not data:
raise ValueError("Invalid or empty JSON body")

# Required fields
reporter_id = data.get("reporter_id")
issue = data.get("issue")
priority = data.get("priority")

if not reporter_id or not issue or not priority:
raise ValueError("Missing required fields: reporter_id, issue, priority")

logger.info(
"Received issue | reporter=%s | priority=%s | issue=%s",
reporter_id,
priority,
issue
)

# -------------------------------------------------
# Simulated issue creation (replace with DB/Jira)
# -------------------------------------------------
issue_id = f"ISSUE-{uuid.uuid4().hex[:8].upper()}"

logger.info("Issue created successfully: %s", issue_id)

#  SUCCESS RESPONSE (Gemini trusts this)
return jsonify({
"issue_id": issue_id,
"assistant_reply": (
f"Your issue has been created successfully. "
f"Reference ID: {issue_id}"
),
"status": "success"
}), 200

except Exception as e:
logger.exception("Issue creation failed")

#  FAILURE RESPONSE (only for real failures)
return jsonify({
"issue_id": None,
"assistant_reply": (
"An internal error occurred while creating your issue. "
"Please try again later."
),
"status": "failed"
}), 500
