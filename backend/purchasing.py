from datetime import date
from typing import List, Dict, Any, Optional

from psycopg2.extras import RealDictCursor

from constant.config import get_db_connection, load_sql_queries_from_directory, PURCHASING_QUERIES_DIR
from constant.error_handling import execute_query
from constant.logger import logger

from backend.inventory import upsert_inventory, get_inventory_by_material_and_location

# Cache queries on startup
QUERIES = load_sql_queries_from_directory(PURCHASING_QUERIES_DIR)


# ==========================================
# PURCHASING LOGIC
# ==========================================


def create_purchase(purchase_number, material_id, location_id, quantity, unit_price, purchase_date):
    logger.debug("purchasing.create_purchase params=%s", (purchase_number, material_id, location_id, quantity, unit_price, purchase_date))
    
    qty_val = float(quantity)
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query(
                "create_purchase",
                QUERIES["create_purchase"],
                (purchase_number, material_id, location_id, qty_val, unit_price, purchase_date),
                cur,
            )
            result = cur.fetchone()
        conn.commit()

    # Update inventory once after purchase commit
    if result:
        upsert_inventory(material_id, location_id, qty_val)

    return dict(result) if result else None


def get_all_purchases() -> List[Dict[str, Any]]:
    logger.debug("purchasing.get_all_purchases")
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("get_all_purchases", QUERIES["get_all_purchases"], None, cur)
            result = cur.fetchall()
    return [dict(row) for row in result]


def get_purchase_by_id(purchase_id: int) -> Optional[Dict[str, Any]]:
    logger.debug("purchasing.get_purchase_by_id params=%s", (purchase_id,))
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("get_purchase_by_id", QUERIES["get_purchase_by_id"], (purchase_id,), cur)
            result = cur.fetchone()
    return dict(result) if result else None


def update_purchase(
    purchase_id: int,
    purchase_number: str,
    material_id: int,
    location_id: int,
    quantity: float,
    unit_price: float,
    purchase_date: date,
) -> Optional[Dict[str, Any]]:
    logger.debug(
        "purchasing.update_purchase params=%s",
        (purchase_id, purchase_number, material_id, location_id, quantity, unit_price, purchase_date),
    )

    old_purchase = get_purchase_by_id(purchase_id)
    if old_purchase:
        # Revert previous purchase quantity from old location/material
        upsert_inventory(
            old_purchase["material_id"], 
            old_purchase["location_id"], 
            -float(old_purchase["quantity"])
            )

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query(
                "update_purchase",
                QUERIES["update_purchase"],
                (purchase_number, material_id, location_id, quantity, unit_price, purchase_date, purchase_id),
                cur,
            )
            result = cur.fetchone()
        conn.commit()

    upsert_inventory(material_id, location_id, float(quantity))

    return dict(result) if result else None


def delete_purchase(purchase_id: int) -> bool:
    logger.debug("purchasing.delete_purchase params=%s", (purchase_id,))

    old_purchase = get_purchase_by_id(purchase_id)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_query("delete_purchase", QUERIES["delete_purchase"], (purchase_id,), cur)
            deleted = cur.fetchone()
        conn.commit()

    upsert_inventory(
        old_purchase["material_id"], 
        old_purchase["location_id"], 
        -float(old_purchase["quantity"])
        )
    
    return bool(deleted)
