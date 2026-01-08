"""
Issue Management API
Compatible with Google Conversational Agents (Vertex AI tools)

Guarantees:
- Always returns HTTP 200
- Always returns valid JSON schema
- Never crashes the agent
"""

from __future__ import annotations

import json
import os
import traceback
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Tuple

from google.cloud import firestore
from google.cloud import pubsub_v1
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
import google.genai as genai


# =====================================================
# Configuration
# =====================================================
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "data-engineering-479617")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

ISSUES_COL = "issues"
USERS_COL = "users"

PUBSUB_TOPIC = "issues-topic"
TASK_QUEUE = "issue-status-queue"

SLA_POLICY: Dict[str, Dict[str, int]] = {
    "P1": {"response_mins": 15, "resolve_mins": 240},
    "P2": {"response_mins": 60, "resolve_mins": 1440},
    "P3": {"response_mins": 240, "resolve_mins": 4320},
    "P4": {"response_mins": 480, "resolve_mins": 10080},
}


# =====================================================
# Clients
# =====================================================
db = firestore.Client(project=PROJECT_ID)
publisher = pubsub_v1.PublisherClient()
tasks_client = tasks_v2.CloudTasksClient()

topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)
queue_path = tasks_client.queue_path(PROJECT_ID, LOCATION, TASK_QUEUE)


# =====================================================
# Helpers
# =====================================================
def utc_now() -> datetime:
    return datetime.utcnow()


def json_response(payload: Dict[str, Any]):
    return (
        json.dumps(payload, ensure_ascii=False),
        200,
        {"Content-Type": "application/json"},
    )


# =====================================================
# Gemini (safe)
# =====================================================
def vertex_client() -> genai.Client:
    return genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
    )


def gemini_reply(issue_text: str) -> str:
    try:
        client = vertex_client()
        resp = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=f"Acknowledge the issue briefly:\n{issue_text}",
        )
        return (resp.text or "").strip() or "Your issue has been logged."
    except Exception:
        return "Your issue has been logged."


# =====================================================
# SLA
# =====================================================
def compute_sla(priority: str) -> Dict[str, Any]:
    policy = SLA_POLICY.get(priority, SLA_POLICY["P3"])
    now = utc_now()
    return {
        "response_due_at": now + timedelta(minutes=policy["response_mins"]),
        "resolve_due_at": now + timedelta(minutes=policy["resolve_mins"]),
        "response_breached": False,
        "resolution_breached": False,
    }


# =====================================================
# Firestore
# =====================================================
def upsert_user(reporter_id: str):
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
) -> Tuple[str, Dict[str, Any]]:
    issue_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
    sla = compute_sla(priority)

    db.collection(ISSUES_COL).document(issue_id).set(
        {
            "reporter_id": reporter_id,
            "issue": issue_text,
            "priority": priority,
            "status": "new",
            "sla": sla,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
    )

    return issue_id, sla


# =====================================================
# Pub/Sub (BQ-SCHEMA COMPATIBLE)
# =====================================================
def publish_issue_event(
    issue_id: str,
    old_status: str | None,
    new_status: str,
    priority: str,
    source: str,
):
    """
    EXACT MATCH to BigQuery issues_status_history schema
    """
    message = {
        "issue_id": issue_id,
        "old_status": old_status,
        "new_status": new_status,
        "priority": priority,
        "source": source,
        "changed_at": utc_now().isoformat() + "Z",
    }

    publisher.publish(
        topic_path,
        json.dumps(message).encode("utf-8")
    ).result()


# =====================================================
# Cloud Tasks (time-based automation)
# =====================================================
def schedule_task(url: str, payload: Dict[str, Any], run_at: datetime):
    ts = timestamp_pb2.Timestamp()
    ts.FromDatetime(run_at)

    task = {
        "http_request": {
            "http_method": tasks_v2.HttpMethod.POST,
            "url": url,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(payload).encode(),
        },
        "schedule_time": ts,
    }

    tasks_client.create_task(parent=queue_path, task=task)


def schedule_status_flow(issue_id: str):
    """
    Automatic lifecycle:
    new -> assigned -> in_progress -> completed
    """
    base_url = f"https://{LOCATION}-{PROJECT_ID}.cloudfunctions.net/update_issue_status"

    schedule_task(base_url, {"issue_id": issue_id, "status": "assigned"}, utc_now() + timedelta(minutes=5))
    schedule_task(base_url, {"issue_id": issue_id, "status": "in_progress"}, utc_now() + timedelta(minutes=7))
    schedule_task(base_url, {"issue_id": issue_id, "status": "completed"}, utc_now() + timedelta(minutes=12))


# =====================================================
# HTTP Entrypoints
# =====================================================
def submit_issue(request):
    try:
        body = request.get_json(silent=True) or {}

        reporter_id = (body.get("reporter_id") or "").strip()
        issue_text = (body.get("issue") or "").strip()
        priority = (body.get("priority") or "P3").upper()

        if not reporter_id or len(issue_text) < 5:
            return json_response({"status": "failed"})

        upsert_user(reporter_id)

        issue_id, _ = create_issue(reporter_id, issue_text, priority)

        #  INITIAL EVENT (new)
        publish_issue_event(
            issue_id=issue_id,
            old_status=None,
            new_status="new",
            priority=priority,
            source="submit_issue",
        )

        schedule_status_flow(issue_id)

        return json_response(
            {
                "issue_id": issue_id,
                "status": "created",
                "assistant_reply": gemini_reply(issue_text),
            }
        )

    except Exception:
        traceback.print_exc()
        return json_response({"status": "failed"})


def update_issue_status(request):
    try:
        body = request.get_json()

        issue_ref = db.collection(ISSUES_COL).document(body["issue_id"])
        snap = issue_ref.get()

        old_status = snap.get("status")

        issue_ref.update(
            {
                "status": body["status"],
                "updated_at": firestore.SERVER_TIMESTAMP,
            }
        )

        #  LIFECYCLE EVENT
        publish_issue_event(
            issue_id=body["issue_id"],
            old_status=old_status,
            new_status=body["status"],
            priority=snap.get("priority"),
            source="cloud_tasks",
        )

        return json_response({"ok": True})

    except Exception:
        traceback.print_exc()
        return json_response({"ok": False})
