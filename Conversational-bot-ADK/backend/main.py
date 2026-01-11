"""
Issue Management Tool
ADK-compatible tool for Vertex AI Agents

Guarantees:
- Never throws uncaught exceptions
- Always returns structured JSON
- Safe for agent execution
"""

from __future__ import annotations

import json
import os
import traceback
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict

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
# Core Logic
# =====================================================
def upsert_user(reporter_id: str):
    db.collection(USERS_COL).document(reporter_id).set(
        {
            "last_seen_at": firestore.SERVER_TIMESTAMP,
            "created_at": firestore.SERVER_TIMESTAMP,
        },
        merge=True,
    )


def create_issue(reporter_id: str, issue_text: str, priority: str):
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

    return issue_id


def publish_issue_event(issue_id: str, old_status: str | None, new_status: str, priority: str, source: str):
    message = {
        "issue_id": issue_id,
        "old_status": old_status,
        "new_status": new_status,
        "priority": priority,
        "source": source,
        "changed_at": utc_now().isoformat() + "Z",
    }

    publisher.publish(topic_path, json.dumps(message).encode()).result()


def schedule_status_flow(issue_id: str):
    base_url = f"https://{LOCATION}-{PROJECT_ID}.cloudfunctions.net/update_issue_status"

    def schedule(run_in_min: int, status: str):
        ts = timestamp_pb2.Timestamp()
        ts.FromDatetime(utc_now() + timedelta(minutes=run_in_min))

        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": base_url,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "issue_id": issue_id,
                    "status": status
                }).encode(),
            },
            "schedule_time": ts,
        }

        tasks_client.create_task(parent=queue_path, task=task)

    schedule(5, "assigned")
    schedule(7, "in_progress")
    schedule(12, "completed")


# =====================================================
# ADK TOOLS
# =====================================================
def submit_issue_tool(
    reporter_id: str,
    issue: str,
    priority: str = "P3",
) -> Dict[str, Any]:
    """
    Tool: Submit an issue and trigger lifecycle automation
    """
    try:
        if not reporter_id or not issue or len(issue) < 5:
            return {"status": "failed", "reason": "Invalid input"}

        priority = priority.upper()

        upsert_user(reporter_id)
        issue_id = create_issue(reporter_id, issue, priority)

        publish_issue_event(
            issue_id=issue_id,
            old_status=None,
            new_status="new",
            priority=priority,
            source="adk_agent",
        )

        schedule_status_flow(issue_id)

        return {
            "status": "created",
            "issue_id": issue_id,
            "assistant_reply": gemini_reply(issue),
        }

    except Exception:
        traceback.print_exc()
        return {"status": "failed"}


def get_issue_status_tool(issue_id: str) -> Dict[str, Any]:
    """
    Tool: Fetch current issue status
    """
    try:
        snap = db.collection(ISSUES_COL).document(issue_id).get()

        if not snap.exists:
            return {"status": "not_found", "issue_id": issue_id}

        data = snap.to_dict()

        return {
            "issue_id": issue_id,
            "current_status": data.get("status"),
            "priority": data.get("priority"),
            "last_updated_at": (
                data.get("updated_at").isoformat()
                if data.get("updated_at")
                else None
            ),
        }

    except Exception:
        traceback.print_exc()
        return {"status": "failed"}
