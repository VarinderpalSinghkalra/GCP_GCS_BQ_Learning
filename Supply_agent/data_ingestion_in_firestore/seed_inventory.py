from google.cloud import firestore

db = firestore.Client()

items = [
    {"id": "screws", "name": "screws", "quantity": 2500, "unit": "pcs"},
    {"id": "bolts", "name": "bolts", "quantity": 1800, "unit": "pcs"},
    {"id": "nuts", "name": "nuts", "quantity": 3000, "unit": "pcs"},
    {"id": "washers", "name": "washers", "quantity": 2200, "unit": "pcs"},
    {"id": "nails", "name": "nails", "quantity": 5000, "unit": "pcs"},
    {"id": "hinges", "name": "hinges", "quantity": 400, "unit": "pcs"},
    {"id": "anchors", "name": "anchors", "quantity": 900, "unit": "pcs"},
    {"id": "rivets", "name": "rivets", "quantity": 1200, "unit": "pcs"},
    {"id": "clamps", "name": "clamps", "quantity": 350, "unit": "pcs"},
    {"id": "brackets", "name": "brackets", "quantity": 800, "unit": "pcs"},
    {"id": "springs", "name": "springs", "quantity": 650, "unit": "pcs"},
    {"id": "gaskets", "name": "gaskets", "quantity": 1400, "unit": "pcs"},
    {"id": "o_rings", "name": "o_rings", "quantity": 2000, "unit": "pcs"},
    {"id": "bearings", "name": "bearings", "quantity": 300, "unit": "pcs"},
    {"id": "couplings", "name": "couplings", "quantity": 270, "unit": "pcs"},
    {"id": "valves", "name": "valves", "quantity": 180, "unit": "pcs"},
    {"id": "pipes", "name": "pipes", "quantity": 500, "unit": "meters"},
    {"id": "fittings", "name": "fittings", "quantity": 1200, "unit": "pcs"},
    {"id": "cables", "name": "cables", "quantity": 1000, "unit": "meters"},
    {"id": "switches", "name": "switches", "quantity": 600, "unit": "pcs"},
    {"id": "connectors", "name": "connectors", "quantity": 1600, "unit": "pcs"},
]

for item in items:
    db.collection("inventory").document(item["id"]).set(item)

print("Inventory seeded successfully with 20+ items.")
