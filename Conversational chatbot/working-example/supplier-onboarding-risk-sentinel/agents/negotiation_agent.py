"""
Negotiation Agent
=================
This module contains ONLY advisory logic.
It NEVER approves or rejects suppliers.
"""

from typing import List


def commercial_suggestion(context: dict) -> dict | None:
    """
    Supplier-level advisory suggestion.
    Used during supplier onboarding when a quotation is received.
    """
    quotation_gcs_uri = context.get("quotation_gcs_uri")
    supplier_id = context.get("supplier_id")

    if not quotation_gcs_uri:
        return None

    return {
        "suggested_action": "NEGOTIATE",
        "recommended_supplier": supplier_id,
        "reason": "Quotation received; RFQ negotiation pending",
        "negotiation_hint": (
            "Wait for additional supplier quotations or negotiate "
            "on price and delivery timeline"
        )
    }


def negotiate_multiple_quotes(quotes: List[object]) -> dict:
    """
    RFQ-level negotiation.
    Compares multiple supplier quotations and recommends the best one.
    """

    if not quotes or len(quotes) < 2:
        return {
            "status": "INSUFFICIENT_QUOTES",
            "message": "At least two quotations are required"
        }

    # Sort by price, then delivery days
    sorted_quotes = sorted(
        quotes,
        key=lambda q: (q.price, q.delivery_days)
    )

    best = sorted_quotes[0]

    return {
        "recommended_supplier": best.supplier_id,
        "reason": "Lowest price with acceptable delivery",
        "comparison": [
            {
                "supplier_id": q.supplier_id,
                "price": q.price,
                "delivery_days": q.delivery_days
            }
            for q in sorted_quotes
        ],
        "negotiation_hint": (
            f"Ask other suppliers to match price {best.price} "
            f"or improve delivery below {best.delivery_days} days"
        )
    }
