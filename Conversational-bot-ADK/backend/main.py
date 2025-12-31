"""
Issue Management Backend
Cloud Functions Gen2 / Cloud Run SAFE version

Fixes:
- Lazy Firestore initialization (prevents PORT=8080 startup failure)
- Always returns HTTP 200
- Agent & ADK compatible
"""

from __future__ import annotations

import json
import os
import traceback
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from google.cloud import firestore
from google import genai


# =====================================================
# Configuration
# =====================================================
PROJECT_ID: str = os.getenv(
    "GOOGLE_CLOUD_PROJECT", "data-engineering-479617"
)
LOCATION: str = os.getenv("GCP_LOCATION", "us-central1")

GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

ISSUES_COL: str = os.getenv("ISSUES_COL", "issues")
USERS_COL: str = os.getenv("USERS_COL", "users")

SLA_POLICY: Dict[str, Dict[str, int]] = {
    "P1": {"response_mins": 15, "resolve_mins": 240},
    "P2": {"response_mins": 60, "resolve_mins": 1440},
    "P3": {"response_mins": 240, "resolve_mins": 4320},
    "P4": {"response_mins": 480, "resolve_mins": 10080},
}


# =====================================================
# Lazy clients (IMPORTANT)
# =====================================================
_firestore_db = None
_genai_client = None


def get_db():
    """Lazy Firestore client (Cloud Run safe)."""
    global _firestore_db
    if _firestore_db is None:
        _firestore_db = firestore.Client(project=PROJECT_ID)
    return _firestore_db


def get_genai_client():
    """Lazy Gemini client."""
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=LOCATION,
        )
    return _genai_client


# =====================================================
# Helpers
# =====================================================
def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def compute_sla(priority: str) -> Dict[str, Any]:
    policy = SLA_POLICY.get(priority, SLA_POLICY["P3"])
    now = utc_now()
    return {
        "response_due_at": now + timedelta(minutes=policy["response_mins"]),
        "resolve_due_at": now + timedelta(minutes=policy["resolve_mins"]),
        "breach": False,
    }


def json_response(payload: Dict[str, Any]):
    """ALWAYS return HTTP 200 for agents."""
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


def gemini_reply(issue_text: str) -> str:
    """Safe Gemini call. Never crashes."""
    try:
        client = get_genai_client()
        resp = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=(
                "You are a support assistant. "
                "Provide a concise and helpful response.\n\n"
                f"Issue: {issue_text}"
            ),
        )
        return (resp.text or "").strip() or "Your issue has been logged."
    except Exception:
        traceback.print_exc()
        return "Your issue has been logged. Our support team will follow up."


def upsert_user(reporter_id: str) -> None:
    db = get_db()
    db.collection(USERS_COL).document(reporter_id).set(
        {
            "last_seen_at": firestore.SERVER_TIMESTAMP,
            "created_at": firestore.SERVER_TIMESTAMP,
        },
        merge=True,
    )


def create_issue(
    reporter_id: str,
    issue_text: str,
    priority: str,
) -> str:
    db = get_db()
    issue_id = f"INC-{uuid.uuid4().hex[:8].upper()}"

    issue_doc = {
        "reporter_id": reporter_id,
        "issue": issue_text,
        "priority": priority,
        "status": "new",
        "sla": compute_sla(priority),
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
    }

    db.collection(ISSUES_COL).document(issue_id).set(issue_doc)
    return issue_id


# =====================================================
# Entry Point
# =====================================================
def submit_issue(request):
    # CORS preflight
    if request.method == "OPTIONS":
        return json_response({})

    try:
        body = request.get_json(silent=True) or {}

        reporter_id = (body.get("reporter_id") or "").strip()
        issue_text = (body.get("issue") or "").strip()
        priority = (body.get("priority") or "P3").upper()

        if priority not in {"P1", "P2", "P3", "P4"}:
            priority = "P3"

        if not reporter_id or len(issue_text) < 5:
            return json_response(
                {
                    "issue_id": "N/A",
                    "status": "failed",
                    "assistant_reply": (
                        "Invalid input. Please provide reporter_id "
                        "and a valid issue description."
                    ),
                }
            )

        upsert_user(reporter_id)
        issue_id = create_issue(reporter_id, issue_text, priority)
        assistant_reply = gemini_reply(issue_text)

        return json_response(
            {
                "issue_id": issue_id,
                "status": "created",
                "assistant_reply": assistant_reply,
            }
        )

    except Exception:
        traceback.print_exc()
        return json_response(
            {
                "issue_id": "ERROR",
                "status": "failed",
                "assistant_reply": (
                    "An internal error occurred, but your issue was received."
                ),
            }
        )
