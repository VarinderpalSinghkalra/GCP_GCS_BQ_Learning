from google.adk.tools import tool
from .db import get_inventory_by_name_or_sku


@tool
def search_inventory(name_or_sku: str) -> dict:
    """
    Search inventory items by name or SKU.
    """
    results = get_inventory_by_name_or_sku(name_or_sku)

    if not results:
        return {
            "status": "NOT_FOUND",
            "items": []
        }

    return {
        "status": "FOUND",
        "items": results
    }
