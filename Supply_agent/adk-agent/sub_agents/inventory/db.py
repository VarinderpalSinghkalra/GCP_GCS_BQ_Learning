from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/inventory_db"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def get_inventory_by_name_or_sku(name_or_sku: str):
    query = text("""
        SELECT item_id, item_name, sku, quantity, warehouse_id, status, last_updated
        FROM inventory
        WHERE item_name ILIKE :value OR sku ILIKE :value
    """)

    with SessionLocal() as session:
        result = session.execute(
            query,
            {"value": f"%{name_or_sku}%"}
        ).mappings().all()

    return [dict(row) for row in result]
