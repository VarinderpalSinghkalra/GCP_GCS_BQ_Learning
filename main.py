import os
import json
import uuid
import traceback
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

from google.cloud import firestore
from google import genai

# -----------------------------
# Config
# -----------------------------
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "platform-support-analyst-57565")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-004")

ENABLE_EMBEDDINGS = os.getenv("ENABLE_EMBEDDINGS", "false").lower() == "true"

ISSUES_COL = os.getenv("ISSUES_COL", "issues")
USERS_COL = os.getenv("USERS_COL", "users")

SLA_POLICY = {
    "P1": {"response_mins": 15, "resolve_mins": 240},
    "P2": {"response_mins": 60, "resolve_mins": 1440},
    "P3": {"response_mins": 240, "resolve_mins": 4320},
    "P4": {"response_mins": 480, "resolve_mins": 10080},
}

db = firestore.Client(project=PROJECT_ID)

# -----------------------------
# Helpers
# -----------------------------
def _utc_now():
    return datetime.now(timezone.utc)

def _compute_sla(priority: str):
    p = SLA_POLICY.get(priority, SLA_POLICY["P3"])
    now = _utc_now()
    return {
        "response_due_at": now + timedelta(minutes=p["response_mins"]),
        "resolve_due_at": now + timedelta(minutes=p["resolve_mins"]),
        "breach": False,
    }

def _json_response(payload: Dict[str, Any]):
    return (
        json.dumps(payload, ensure_ascii=False),
        200,
        {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    )

def _vertex_client():
    return genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

def _gemini_reply(issue_text: str) -> str:
    try:
        client = _vertex_client()
        resp = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=f"Provide a clear support response:\n\n{issue_text}",
        )
        return (resp.text or "").strip() or "Your issue has been logged."
    except Exception:
        traceback.print_exc()
        return "Your issue has been logged. Our team will follow up shortly."

def _upsert_user(reporter_id: str):
    db.collection(USERS_COL).document(reporter_id).set(
        {
            "last_seen_at": firestore.SERVER_TIMESTAMP,
            "created_at": firestore.SERVER_TIMESTAMP,
        },
        merge=True,
    )

def _create_issue(reporter_id: str, issue_text: str, priority: str) -> str:
    issue_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
    doc = {
        "reporter_id": reporter_id,
        "issue": issue_text,
        "priority": priority,
        "status": "new",
        "sla": _compute_sla(priority),
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
    }
    db.collection(ISSUES_COL).document(issue_id).set(doc)
    return issue_id

# -----------------------------
# Entry point
# -----------------------------
def submit_issue(request):
    if request.method == "OPTIONS":
        return _json_response({})

    try:
        body = request.get_json(silent=True) or {}
        reporter_id = (body.get("reporter_id") or "").strip()
        issue_text = (body.get("issue") or "").strip()
        priority = (body.get("priority") or "P3").upper()

        if priority not in ("P1", "P2", "P3", "P4"):
            priority = "P3"

        if not reporter_id or len(issue_text) < 5:
            return _json_response({
                "issue_id": "N/A",
                "status": "failed",
                "assistant_reply": "Invalid input. Please provide reporter_id and issue details."
            })

        _upsert_user(reporter_id)
        issue_id = _create_issue(reporter_id, issue_text, priority)
        assistant_reply = _gemini_reply(issue_text)

        return _json_response({
            "issue_id": issue_id,
            "status": "created",
            "assistant_reply": assistant_reply,
        })

    except Exception as e:
        traceback.print_exc()
        return _json_response({
            "issue_id": "ERROR",
            "status": "failed",
            "assistant_reply": "An internal error occurred, but your request was received."
        })
