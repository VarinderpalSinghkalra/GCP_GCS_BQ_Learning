import os
import json
import uuid
import traceback
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

from flask import Request

# -------------------------------------------------
# Environment (SAFE)
# -------------------------------------------------
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "platform-support-analyst-57565")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")

ISSUES_COL = os.getenv("ISSUES_COL", "issues")
USERS_COL = os.getenv("USERS_COL", "users")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
ENABLE_GEMINI = os.getenv("ENABLE_GEMINI", "false").lower() == "true"
ENABLE_EMBEDDINGS = os.getenv("ENABLE_EMBEDDINGS", "false").lower() == "true"

# -------------------------------------------------
# SLA Policy
# -------------------------------------------------
SLA_POLICY = {
"P1": {"response_mins": 15, "resolve_mins": 240},
"P2": {"response_mins": 60, "resolve_mins": 1440},
"P3": {"response_mins": 240, "resolve_mins": 4320},
"P4": {"response_mins": 480, "resolve_mins": 10080},
}

# -------------------------------------------------
# Lazy clients (CRITICAL for Gen-2)
# -------------------------------------------------
_firestore = None

def get_firestore():
global _firestore
if _firestore is None:
from google.cloud import firestore
_firestore = firestore.Client()
return _firestore

def get_gemini_client():
from google import genai
return genai.Client(
vertexai=True,
project=PROJECT_ID,
location=LOCATION,
)

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def utc_now():
return datetime.now(timezone.utc)

def compute_sla(priority: str):
p = SLA_POLICY.get(priority, SLA_POLICY["P3"])
now = utc_now()
return {
"response_due_at": now + timedelta(minutes=p["response_mins"]),
"resolve_due_at": now + timedelta(minutes=p["resolve_mins"]),
"breach": False,
}

def json_response(payload: Dict[str, Any], status: int = 200):
return (
json.dumps(payload, ensure_ascii=False),
status,
{"Content-Type": "application/json"},
)

def parse_json(request: Request):
try:
body = request.get_json(silent=True)
if isinstance(body, dict):
return body, None
return None, "Invalid JSON body"
except Exception:
return None, "Invalid JSON body"

# -------------------------------------------------
# Gemini (SAFE)
# -------------------------------------------------
def gemini_reply(issue_text: str) -> str:
if not ENABLE_GEMINI:
return "Your issue has been logged. Our team will review it shortly."

try:
client = get_gemini_client()
resp = client.models.generate_content(
model=GEMINI_MODEL,
contents=f"You are a support assistant.\nUser issue: {issue_text}",
)
return (resp.text or "").strip() or "Thanks, we are looking into this."
except Exception:
traceback.print_exc()
return "Thanks, we are looking into this."

# -------------------------------------------------
# Core operations
# -------------------------------------------------
def upsert_user(reporter_id: str):
db = get_firestore()
db.collection(USERS_COL).document(reporter_id).set(
{"last_seen_at": utc_now()},
merge=True,
)

def create_issue(reporter_id: str, issue_text: str, priority: str) -> str:
db = get_firestore()
issue_id = f"ISSUE-{uuid.uuid4().hex[:8].upper()}"

doc = {
"reporter_id": reporter_id,
"issue": issue_text,
"priority": priority,
"status": "new",
"sla": compute_sla(priority),
"created_at": utc_now(),
"updated_at": utc_now(),
}

db.collection(ISSUES_COL).document(issue_id).set(doc)
return issue_id

# -------------------------------------------------
# ✅ Gen-2 Cloud Function Entry Point
# -------------------------------------------------
def submit_issue(request: Request):
if request.method == "OPTIONS":
return json_response({}, 204)

if request.method != "POST":
return json_response({"error": "Method not allowed"}, 405)

body, err = parse_json(request)
if err:
return json_response({"error": err}, 400)

reporter_id = (body.get("reporter_id") or "").strip()
issue_text = (body.get("issue") or "").strip()
priority = (body.get("priority") or "P3").upper()

if not reporter_id:
return json_response({"error": "reporter_id is required"}, 400)
if not issue_text or len(issue_text) < 5:
return json_response({"error": "issue must be at least 5 characters"}, 400)

try:
upsert_user(reporter_id)
issue_id = create_issue(reporter_id, issue_text, priority)
reply = gemini_reply(issue_text)

return json_response(
{
"issue_id": issue_id,
"status": "new",
"assistant_reply": reply,
},
200,
)
except Exception as e:
traceback.print_exc()
return json_response({"error": str(e)}, 500)
