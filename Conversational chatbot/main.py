import logging
import uuid
from flask import Flask, request, jsonify

# -------------------------------------------------
# App setup
# -------------------------------------------------
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# Health check (recommended for Cloud Run)
# -------------------------------------------------
@app.route("/", methods=["GET"])
def health():
return "OK", 200


# -------------------------------------------------
# Create Issue API (Gemini Tool)
# -------------------------------------------------
@app.route("/createIssue", methods=["POST"])
def create_issue():
try:
data = request.get_json(silent=True)

if not data:
raise ValueError("Request body is empty or invalid JSON")

# Required fields
reporter_id = data.get("reporter_id")
issue = data.get("issue")
priority = data.get("priority")

if not reporter_id or not issue or not priority:
raise ValueError("Missing required fields: reporter_id, issue, priority")

logger.info(
"Creating issue | reporter=%s | priority=%s | issue=%s",
reporter_id,
priority,
issue
)

# -------------------------------------------------
# TODO: Replace this with DB / Jira / ServiceNow call
# -------------------------------------------------
issue_id = f"ISSUE-{uuid.uuid4().hex[:8].upper()}"

logger.info("Issue created successfully: %s", issue_id)

# ✅ SUCCESS RESPONSE (Gemini trusts this)
return jsonify({
"issue_id": issue_id,
"assistant_reply": f"Your issue has been created successfully. Reference ID: {issue_id}",
"status": "success"
}), 200

except Exception as e:
logger.exception("Issue creation failed")

# ❌ FAILURE RESPONSE (used only when truly broken)
return jsonify({
"issue_id": None,
"assistant_reply": "An internal error occurred while creating your issue. Please try again later.",
"status": "failed"
}), 500


# -------------------------------------------------
# Entry point for Cloud Run
# -------------------------------------------------
if __name__ == "__main__":
app.run(host="0.0.0.0", port=8080)
