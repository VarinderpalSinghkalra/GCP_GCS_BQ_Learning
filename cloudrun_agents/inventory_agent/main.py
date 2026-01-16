from fastapi import FastAPI, HTTPException
import psycopg2
import os
import uuid

app = FastAPI()

# ---- DB config (Cloud Run / Local) ----
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_PORT = os.environ.get("DB_PORT", "5432")


def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )


@app.get("/")
def health():
    return {"status": "inventory-agent ok"}


# ---------- Inventory Search ----------
@app.get("/inventory/search")
def search(name: str):
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT item_id, item_name, sku, quantity, price, currency
            FROM inventory
            WHERE item_name ILIKE %s
              AND status = 'AVAILABLE'
            """,
            (f"%{name}%",)
        )

        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Item not found")

        return {
            "item_id": str(row[0]),   # UUID → string
            "item_name": row[1],
            "sku": row[2],
            "quantity": row[3],
            "unit_price": float(row[4]),
            "currency": row[5]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Inventory Cost ----------
@app.get("/inventory/cost")
def cost(item_id: str, quantity: int):
    try:
        # validate UUID
        uuid.UUID(item_id)

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT price, currency, quantity
            FROM inventory
            WHERE item_id = %s
            """,
            (item_id,)
        )

        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Item not found")

        unit_price = float(row[0])
        available_qty = row[2]

        if quantity > available_qty:
            raise HTTPException(
                status_code=400,
                detail="Insufficient inventory"
            )

        total_cost = unit_price * quantity

        return {
            "item_id": item_id,
            "requested_quantity": quantity,
            "unit_price": unit_price,
            "total_cost": total_cost,
            "currency": row[1]
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item_id (UUID required)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
