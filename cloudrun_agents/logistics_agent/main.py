from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/")
def health():
    return {"status": "logistics-agent ok"}


@app.post("/logistics/execute")
def execute(payload: dict):
    order_id = payload.get("order_id")
    approved = payload.get("approved")

    if not order_id:
        raise HTTPException(status_code=400, detail="order_id is required")

    if approved is not True:
        raise HTTPException(status_code=400, detail="Order not approved")

    # Simulate shipment creation
    return {
        "order_id": order_id,
        "shipment_id": f"SHIP-{order_id[:8]}",
        "status": "DISPATCHED"
    }
