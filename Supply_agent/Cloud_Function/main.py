"""
Supply Chain Ticket API
Compatible with Google Conversational Agents (Vertex AI / ADK tools)

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
from datetime import datetime
from typing import Any, Dict

from google.cloud import firestore
import google.genai as genai


# =====================================================
# Configuration
# =====================================================
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "data-engineering-479617")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

ORDERS_COL = "supply_orders"


# =====================================================
# Clients
# =====================================================
db = firestore.Client(project=PROJECT_ID)


# =====================================================
# Helpers
# =====================================================
def utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def json_response(payload: Dict[str, Any]):
    return (
        json.dumps(payload, ensure_ascii=False),
        200,
        {"Content-Type": "application/json"},
    )


# =====================================================
# Gemini (safe + optional)
# =====================================================
def vertex_client() -> genai.Client:
    return genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
    )


def gemini_ack(text: str) -> str:
    try:
        client = vertex_client()
        resp = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=f"Acknowledge this supply request briefly:\n{text}",
        )
        return (resp.text or "").strip() or "Your supply request has been logged."
    except Exception:
        return "Your supply request has been logged."


# =====================================================
# Ticket Creation
# =====================================================
def create_supply_ticket(
    requester_id: str,
    item_id: str,
    quantity: int,
) -> str:
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    db.collection(ORDERS_COL).document(order_id).set(
        {
            "requester_id": requester_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "new",

            # Filled by agents later
            "inventory": None,
            "estimated_cost": None,
            "approval_status": None,
            "shipment": None,

            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
    )

    return order_id


# =====================================================
# HTTP Entrypoints (Agent-Friendly)
# =====================================================
def submit_supply_request(request):
    """
    Conversational entrypoint
    """
    try:
        body = request.get_json(silent=True) or {}

        requester_id = (body.get("requester_id") or "").strip()
        item_id = (body.get("item_id") or "").strip()
        quantity = int(body.get("quantity") or 0)

        if not requester_id or not item_id or quantity <= 0:
            return json_response({"status": "failed"})

        order_id = create_supply_ticket(
            requester_id=requester_id,
            item_id=item_id,
            quantity=quantity,
        )

        return json_response({
            "order_id": order_id,
            "status": "created",
            "assistant_reply": gemini_ack(
                f"Item {item_id}, quantity {quantity}"
            ),
        })

    except Exception:
        traceback.print_exc()
        return json_response({"status": "failed"})


def update_supply_status(request):
    """
    Used by:
    - Inventory Agent
    - Finance Agent (A2A)
    - Logistics Agent
    """
    try:
        body = request.get_json(silent=True) or {}

        order_id = body.get("order_id")
        updates = body.get("updates", {})

        if not order_id or not updates:
            return json_response({"ok": False})

        db.collection(ORDERS_COL).document(order_id).update(
            {
                **updates,
                "updated_at": firestore.SERVER_TIMESTAMP,
            }
        )

        return json_response({"ok": True})

    except Exception:
        traceback.print_exc()
        return json_response({"ok": False})


def get_supply_status(request):
    """
    Agent-safe status lookup
    """
    try:
        order_id = (
            request.args.get("order_id")
            or (request.get_json(silent=True) or {}).get("order_id")
        )

        if not order_id:
            return json_response({
                "status": "failed",
                "message": "order_id is required",
            })

        snap = db.collection(ORDERS_COL).document(order_id).get()

        if not snap.exists:
            return json_response({
                "status": "not_found",
                "order_id": order_id,
            })

        data = snap.to_dict()

        return json_response({
            "order_id": order_id,
            "current_status": data.get("status"),
            "item_id": data.get("item_id"),
            "quantity": data.get("quantity"),
            "inventory": data.get("inventory"),
            "estimated_cost": data.get("estimated_cost"),
            "approval_status": data.get("approval_status"),
            "shipment": data.get("shipment"),
        })

    except Exception:
        traceback.print_exc()
        return json_response({
            "status": "failed",
            "message": "Unable to fetch supply status",
        })
