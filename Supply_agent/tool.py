import psycopg2
from psycopg2.pool import SimpleConnectionPool

_POOL = None


def get_pool():
    global _POOL
    if _POOL is None:
        _POOL = SimpleConnectionPool(
            minconn=1,
            maxconn=5,
            host="127.0.0.1",
            port=5432,
            database="inventory_db",
            user="postgres",
            password="admin",
            connect_timeout=5
        )
    return _POOL


def get_inventory_by_name(name: str):
    pool = get_pool()              # ← ONLY HERE
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT item_name, sku, quantity, warehouse_id, status
                FROM inventory
                WHERE LOWER(item_name) = LOWER(%s)
                   OR LOWER(sku) = LOWER(%s)
            """, (name, name))

            rows = cur.fetchall()

        if not rows:
            return f"There are no {name} found in the inventory."

        return [
            {
                "item_name": r[0],
                "sku": r[1],
                "quantity": r[2],
                "warehouse_id": r[3],
                "status": r[4]
            }
            for r in rows
        ]
    finally:
        pool.putconn(conn)
