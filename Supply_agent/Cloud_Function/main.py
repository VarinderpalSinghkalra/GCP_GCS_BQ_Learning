"""
Supply Chain Ticket & Intelligence API
Compatible with Google Vertex AI Conversational Agents (ADK tools)

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
INVENTORY_COL = "inventory"
PRICING_COL = "pricing"


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
# Gemini (Optional / Safe)
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
        return (resp.text or "").strip() or "Your request has been logged."
    except Exception:
        return "Your request has been logged."


# =====================================================
# Inventory (Read-only)
# =====================================================
def get_inventory_item(request):
    """
    Used by InventoryAgent to answer supply questions
    """
    try:
        body = request.get_json(silent=True) or {}
        item = (body.get("item") or "").strip().lower()

        if not item:
            return json_response({"available": False})

        snap = (
            db.collection(INVENTORY_COL)
            .where("name", "==", item)
            .limit(1)
            .get()
        )

        if not snap:
            return json_response({
                "item": item,
                "available": False,
            })

        data = snap[0].to_dict()

        return json_response({
            "item": data["name"],
            "available": True,
            "quantity": data["quantity"],
            "unit": data.get("unit", "pcs"),
        })

    except Exception:
        traceback.print_exc()
        return json_response({"available": False})


# =====================================================
# Finance
# =====================================================
def estimate_cost(request):
    """
    Used by FinanceAgent for estimation
    """
    try:
        body = request.get_json(silent=True) or {}
        item_id = body.get("item_id")
        quantity = int(body.get("quantity", 0))

        if not item_id or quantity <= 0:
            return json_response({"estimated_cost": None})

        snap = db.collection(PRICING_COL).document(item_id).get()
        if not snap.exists:
            return json_response({"estimated_cost": None})

        unit_price = snap.get("unit_price")
        total = unit_price * quantity

        return json_response({
            "item_id": item_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "estimated_cost": total,
        })

    except Exception:
        traceback.print_exc()
        return json_response({"estimated_cost": None})


def approve_budget(request):
    """
    Used by FinanceAgent (A2A or tool)
    """
    try:
        body = request.get_json(silent=True) or {}
        order_id = body.get("order_id")
        approved = bool(body.get("approved", False))

        if not order_id:
            return json_response({"approved": False})

        db.collection(ORDERS_COL).document(order_id).update({
            "approval_status": {
                "approved": approved,
                "approved_at": firestore.SERVER_TIMESTAMP,
            },
            "status": "approved" if approved else "rejected",
            "updated_at": firestore.SERVER_TIMESTAMP,
        })

        return json_response({"approved": approved})

    except Exception:
        traceback.print_exc()
        return json_response({"approved": False})


# =====================================================
# Logistics
# =====================================================
def get_shipping_options(request):
    """
    Used by LogisticsAgent for planning
    """
    try:
        return json_response({
            "options": [
                {"carrier": "BlueDart", "eta_days": 2, "cost": 500},
                {"carrier": "Delhivery", "eta_days": 4, "cost": 300},
            ]
        })
    except Exception:
        return json_response({"options": []})


def execute_shipment(request):
    """
    Used by LogisticsAgent after finance approval
    """
    try:
        body = request.get_json(silent=True) or {}
        order_id = body.get("order_id")
        carrier = body.get("carrier")

        if not order_id or not carrier:
            return json_response({"shipped": False})

        db.collection(ORDERS_COL).document(order_id).update({
            "shipment": {
                "carrier": carrier,
                "tracking_id": f"TRK-{uuid.uuid4().hex[:6].upper()}",
                "shipped_at": firestore.SERVER_TIMESTAMP,
            },
            "status": "shipped",
            "updated_at": firestore.SERVER_TIMESTAMP,
        })

        return json_response({"shipped": True})

    except Exception:
        traceback.print_exc()
        return json_response({"shipped": False})


# =====================================================
# Ticket APIs
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

        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        db.collection(ORDERS_COL).document(order_id).set({
            "requester_id": requester_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "new",
            "inventory": None,
            "estimated_cost": None,
            "approval_status": None,
            "shipment": None,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
        })

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
    Generic agent update endpoint
    """
    try:
        body = request.get_json(silent=True) or {}
        order_id = body.get("order_id")
        updates = body.get("updates", {})

        if not order_id or not updates:
            return json_response({"ok": False})

        db.collection(ORDERS_COL).document(order_id).update({
            **updates,
            "updated_at": firestore.SERVER_TIMESTAMP,
        })

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
            return json_response({"status": "failed"})

        snap = db.collection(ORDERS_COL).document(order_id).get()
        if not snap.exists:
            return json_response({"status": "not_found"})

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
        return json_response({"status": "failed"})