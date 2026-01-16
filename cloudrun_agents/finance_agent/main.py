from fastapi import FastAPI, HTTPException

app = FastAPI()

APPROVAL_THRESHOLD = 100.0  # INR


@app.get("/")
def health():
    return {"status": "finance-agent ok"}


@app.post("/finance/check")
def finance_check(payload: dict):
    amount = payload.get("amount")

    if amount is None:
        raise HTTPException(status_code=400, detail="amount is required")

    if amount > APPROVAL_THRESHOLD:
        return {
            "approved": False,
            "approval_required": True,
            "threshold": APPROVAL_THRESHOLD
        }

    return {
        "approved": True,
        "approval_required": False
    }
