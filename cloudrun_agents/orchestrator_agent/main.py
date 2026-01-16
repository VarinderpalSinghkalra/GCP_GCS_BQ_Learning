from fastapi import FastAPI, HTTPException
import requests
import os

app = FastAPI()

INV = os.environ.get("INV_URL")
FIN = os.environ.get("FIN_URL")
LOG = os.environ.get("LOG_URL")

TIMEOUT = 5  # seconds


@app.get("/")
def health():
    return {
        "status": "ok",
        "inventory": INV,
        "finance": FIN,
        "logistics": LOG
    }


@app.post("/query")
def run(req: dict):
    try:
        item = req["item"]
        qty = req["quantity"]
        approval = req.get("approval")

        # ---------------- Inventory search ----------------
        inv_resp = requests.get(
            f"{INV}/inventory/search",
            params={"name": item},
            timeout=TIMEOUT
        )

        if inv_resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Inventory service failed"
            )

        inv = inv_resp.json()

        if "item_id" not in inv:
            raise HTTPException(
                status_code=500,
                detail=f"Invalid inventory response: {inv}"
            )

        # ---------------- Cost calculation ----------------
        cost_resp = requests.get(
            f"{INV}/inventory/cost",
            params={
                "item_id": inv["item_id"],
                "quantity": qty
            },
            timeout=TIMEOUT
        )

        if cost_resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Inventory cost calculation failed"
            )

        cost = cost_resp.json()

        if "total_cost" not in cost:
            raise HTTPException(
                status_code=500,
                detail=f"Invalid cost response: {cost}"
            )

        # ---------------- Finance check ----------------
        fin_resp = requests.post(
            f"{FIN}/finance/check",
            json={"amount": cost["total_cost"]},
            timeout=TIMEOUT
        )

        if fin_resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Finance service failed"
            )

        fin = fin_resp.json()

        if fin.get("approval_required") and approval is None:
            return {
                "status": "WAITING_FOR_APPROVAL",
                "total_cost": cost["total_cost"]
            }

        if approval is False:
            return {"status": "REJECTED"}

        # ---------------- Logistics execute ----------------
        log_resp = requests.post(
            f"{LOG}/logistics/execute",
            json={
                "order_id": inv["item_id"],
                "approved": True
            },
            timeout=TIMEOUT
        )

        if log_resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Logistics service failed"
            )

        ship = log_resp.json()

        return {
            "status": "COMPLETED",
            "inventory": inv,
            "cost": cost,
            "finance": fin,
            "logistics": ship
        }

    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Missing field: {str(e)}"
        )

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=504,
            detail=str(e)
        )
