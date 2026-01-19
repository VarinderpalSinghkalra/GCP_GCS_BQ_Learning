"""
Access Request Provisioning Agent

Guarantees:
- Always HTTP 200
- Always valid JSON
- Never crashes the agent
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


# =====================================================
# Configuration
# =====================================================
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "data-engineering-479617")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")

ACCESS_REQUESTS_COL = "access_requests"

ACCESS_PUBSUB_TOPIC = "access-requests-topic"
ACCESS_TASK_QUEUE = "access-request-queue"


# =====================================================
# Clients
# =====================================================
db = firestore.Client(project=PROJECT_ID)
publisher = pubsub_v1.PublisherClient()
tasks_client = tasks_v2.CloudTasksClient()

topic_path = publisher.topic_path(PROJECT_ID, ACCESS_PUBSUB_TOPIC)
queue_path = tasks_client.queue_path(PROJECT_ID, LOCATION, ACCESS_TASK_QUEUE)


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
# Pub/Sub Publisher
# =====================================================
def publish_event(
    request_id: str,
    old_status: str | None,
    new_status: str,
    source: str,
):
    try:
        message = {
            "request_id": request_id,
            "old_status": old_status,
            "new_status": new_status,
            "source": source,
            "changed_at": utc_now().isoformat() + "Z",
        }

        publisher.publish(
            topic_path,
            json.dumps(message).encode("utf-8"),
        ).result()
    except Exception:
        pass


# =====================================================
# Cloud Tasks
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


def schedule_access_flow(request_id: str):
    """
    3-minute lifecycle:
    new -> assigned -> in_progress -> completed
    """
    base_url = (
        f"https://{LOCATION}-{PROJECT_ID}.cloudfunctions.net/"
        "update_access_request_status"
    )

    schedule_task(
        base_url,
        {"request_id": request_id, "status": "assigned"},
        utc_now() + timedelta(minutes=1),
    )

    schedule_task(
        base_url,
        {"request_id": request_id, "status": "in_progress"},
        utc_now() + timedelta(minutes=2),
    )

    schedule_task(
        base_url,
        {"request_id": request_id, "status": "completed"},
        utc_now() + timedelta(minutes=3),
    )


# =====================================================
# Firestore
# =====================================================
def create_access_request(
    user_id: str,
    resource: str,
    access_level: str,
    justification: str,
):
    request_id = f"AR-{uuid.uuid4().hex[:8].upper()}"

    db.collection(ACCESS_REQUESTS_COL).document(request_id).set(
        {
            "user_id": user_id,
            "resource": resource,
            "access_level": access_level,
            "justification": justification,
            "status": "new",
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
    )

    return request_id


# =====================================================
# HTTP Entrypoints (Agent Tools)
# =====================================================
def submit_access_request(request):
    """
    Tool: Create access request
    """
    try:
        body = request.get_json(silent=True) or {}

        user_id = (body.get("user_id") or "").strip()
        resource = (body.get("resource") or "").strip()
        access_level = (body.get("access_level") or "").strip()
        justification = (body.get("justification") or "").strip()

        if not user_id or not resource or not access_level:
            return json_response({"status": "failed"})

        request_id = create_access_request(
            user_id, resource, access_level, justification
        )

        publish_event(
            request_id=request_id,
            old_status=None,
            new_status="new",
            source="submit_access_request",
        )

        schedule_access_flow(request_id)

        return json_response({
            "request_id": request_id,
            "status": "created",
        })

    except Exception:
        traceback.print_exc()
        return json_response({"status": "failed"})


def update_access_request_status(request):
    """
    Cloud Tasks target
    """
    try:
        body = request.get_json()

        ref = db.collection(ACCESS_REQUESTS_COL).document(body["request_id"])
        snap = ref.get()

        old_status = snap.get("status")

        ref.update(
            {
                "status": body["status"],
                "updated_at": firestore.SERVER_TIMESTAMP,
            }
        )

        publish_event(
            request_id=body["request_id"],
            old_status=old_status,
            new_status=body["status"],
            source="cloud_tasks",
        )

        return json_response({"ok": True})

    except Exception:
        traceback.print_exc()
        return json_response({"ok": False})


def get_access_request_status(request):
    """
    Tool: Fetch access request status
    """
    try:
        request_id = (
            request.args.get("request_id")
            or (request.get_json(silent=True) or {}).get("request_id")
        )

        if not request_id:
            return json_response({"status": "failed"})

        snap = db.collection(ACCESS_REQUESTS_COL).document(request_id).get()

        if not snap.exists:
            return json_response({"status": "not_found"})

        data = snap.to_dict()

        return json_response({
            "request_id": request_id,
            "status": data.get("status"),
            "resource": data.get("resource"),
            "access_level": data.get("access_level"),
            "updated_at": (
                data.get("updated_at").isoformat()
                if data.get("updated_at") else None
            ),
        })

    except Exception:
        traceback.print_exc()
        return json_response({"status": "failed"})
