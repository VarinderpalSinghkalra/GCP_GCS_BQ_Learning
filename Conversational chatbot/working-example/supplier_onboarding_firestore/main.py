"""
Supplier Onboarding Management API
Compatible with Google Conversational Agents (Vertex AI tools)

Guarantees:
- Always returns HTTP 200
- Always returns valid JSON
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

SUPPLIER_REQUESTS_COL = "supplier_onboarding_requests"
SUPPLIERS_COL = "suppliers"

PUBSUB_TOPIC = "supplier-onboarding-events"
TASK_QUEUE = "supplier-onboarding-queue"


# =====================================================
# Clients
# =====================================================
db = firestore.Client()
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
# Firestore helpers
# =====================================================
def upsert_supplier(supplier_id: str, supplier_name: str):
    db.collection(SUPPLIERS_COL).document(supplier_id).set(
        {
            "supplier_name": supplier_name,
            "last_seen_at": firestore.SERVER_TIMESTAMP,
            "created_at": firestore.SERVER_TIMESTAMP,
        },
        merge=True,
    )


def create_supplier_onboarding_request(
    supplier_id: str,
    supplier_name: str,
    country: str,
    justification: str,
) -> str:
    request_id = f"SUP-{uuid.uuid4().hex[:8].upper()}"

    db.collection(SUPPLIER_REQUESTS_COL).document(request_id).set(
        {
            "supplier_id": supplier_id,
            "supplier_name": supplier_name,
            "country": country,
            "justification": justification,
            "status": "new",
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
    )

    return request_id


# =====================================================
# Pub/Sub
# =====================================================
def publish_event(request_id: str, old_status: str | None, new_status: str, source: str):
    try:
        publisher.publish(
            topic_path,
            json.dumps({
                "request_id": request_id,
                "old_status": old_status,
                "new_status": new_status,
                "source": source,
                "changed_at": utc_now().isoformat() + "Z",
            }).encode("utf-8"),
        ).result()
    except Exception:
        pass


# =====================================================
# Cloud Tasks
# =====================================================
def schedule_task(url: str, payload: Dict[str, Any], run_at: datetime):
    ts = timestamp_pb2.Timestamp()
    ts.FromDatetime(run_at)

    tasks_client.create_task(
        parent=queue_path,
        task={
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": url,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(payload).encode(),
            },
            "schedule_time": ts,
        },
    )


def schedule_onboarding_flow(request_id: str):
    base_url = (
        f"https://{LOCATION}-{PROJECT_ID}.cloudfunctions.net/"
        "update_supplier_onboarding_status"
    )

    schedule_task(base_url, {"request_id": request_id, "status": "documents_verified"},
                  utc_now() + timedelta(minutes=1))

    schedule_task(base_url, {"request_id": request_id, "status": "compliance_checked"},
                  utc_now() + timedelta(minutes=2))

    schedule_task(base_url, {"request_id": request_id, "status": "approved"},
                  utc_now() + timedelta(minutes=3))


# =====================================================
# Agent-facing HTTP endpoints
# =====================================================
def submit_supplier_onboarding_request(request):
    try:
        body = request.get_json(silent=True) or {}

        supplier_id = body.get("supplier_id", "").strip()
        supplier_name = body.get("supplier_name", "").strip()
        country = body.get("country", "").strip()
        justification = body.get("justification", "").strip()

        if not supplier_id or not supplier_name or not country:
            return json_response({"status": "failed"})

        upsert_supplier(supplier_id, supplier_name)

        request_id = create_supplier_onboarding_request(
            supplier_id, supplier_name, country, justification
        )

        publish_event(request_id, None, "new", "submit_supplier_onboarding_request")
        schedule_onboarding_flow(request_id)

        return json_response({"request_id": request_id, "status": "created"})

    except Exception:
        traceback.print_exc()
        return json_response({"status": "failed"})


def get_supplier_onboarding_status(request):
    try:
        request_id = request.args.get("request_id") or \
                     (request.get_json(silent=True) or {}).get("request_id")

        if not request_id:
            return json_response({"status": "failed"})

        snap = db.collection(SUPPLIER_REQUESTS_COL).document(request_id).get()
        if not snap.exists:
            return json_response({"status": "not_found"})

        data = snap.to_dict()

        return json_response({
            "request_id": request_id,
            "supplier_name": data.get("supplier_name"),
            "status": data.get("status"),
            "country": data.get("country"),
        })

    except Exception:
        traceback.print_exc()
        return json_response({"status": "failed"})


# =====================================================
# INTERNAL (Cloud Tasks only)
# =====================================================
def update_supplier_onboarding_status(request):
    try:
        body = request.get_json()
        ref = db.collection(SUPPLIER_REQUESTS_COL).document(body["request_id"])
        snap = ref.get()

        old_status = snap.get("status")

        ref.update({
            "status": body["status"],
            "updated_at": firestore.SERVER_TIMESTAMP,
        })

        publish_event(body["request_id"], old_status, body["status"], "cloud_tasks")
        return json_response({"ok": True})

    except Exception:
        traceback.print_exc()
        return json_response({"ok": False})
