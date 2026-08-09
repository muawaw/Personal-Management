from typing import List, Dict, Any, Optional

from psycopg2.extras import RealDictCursor

from constant.config import get_db_connection, load_sql_queries_from_directory, INVENTORY_QUERIES_DIR
from constant.error_handling import execute_query
from constant.logger import logger


# Cache queries on startup
QUERIES = load_sql_queries_from_directory(INVENTORY_QUERIES_DIR)


# ==========================================
# INVENTORY LOGIC
# ==========================================


def create_inventory(material_id: int, location_id: int, stock_qty: float) -> Dict[str, Any]:
    logger.debug("inventory.create_inventory params=%s", (material_id, location_id, stock_qty))
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("create_inventory", QUERIES["create_inventory"], (material_id, location_id, stock_qty), cur)
            result = cur.fetchone()
        conn.commit()
    return dict(result)


def get_all_inventory() -> List[Dict[str, Any]]:
    logger.debug("inventory.get_all_inventory")
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("get_all_inventory", QUERIES["get_all_inventory"], None, cur)
            result = cur.fetchall()
    return [dict(row) for row in result]


def get_inventory_by_id(inventory_id: int) -> Optional[Dict[str, Any]]:
    logger.debug("inventory.get_inventory_by_id params=%s", (inventory_id,))
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("get_inventory_by_id", QUERIES["get_inventory_by_id"], (inventory_id,), cur)
            result = cur.fetchone()
    return dict(result) if result else None


def update_inventory(inventory_id: int, material_id: int, location_id: int, stock_qty: float) -> Optional[Dict[str, Any]]:
    logger.debug(
        "inventory.update_inventory params=%s",
        (inventory_id, material_id, location_id, stock_qty),
    )
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("update_inventory", QUERIES["update_inventory"], (material_id, location_id, stock_qty, inventory_id), cur)
            result = cur.fetchone()
        conn.commit()
    return dict(result) if result else None


def adjust_inventory(inventory_id: int, quantity_delta: float) -> Optional[Dict[str, Any]]:
    logger.debug("inventory.adjust_inventory params=%s", (inventory_id, quantity_delta))
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("adjust_inventory", QUERIES["adjust_inventory"], (quantity_delta, inventory_id), cur)
            result = cur.fetchone()
        conn.commit()
    return dict(result) if result else None

def get_inventory_by_material_and_location(material_id: int, location_id: int) -> Optional[Dict[str, Any]]:
    logger.debug("inventory.get_inventory_by_material_and_location params=%s", (material_id, location_id))
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query(
                "get_inventory_by_material_and_location",
                QUERIES["get_inventory_by_material_and_location"],
                (material_id, location_id),
                cur,
            )
            result = cur.fetchone()
    return dict(result) if result else None


def update_inventory_stock(material_id: int, location_id: int, qty_change: float) -> None:
    """
    Adjusts stock level. If inventory record doesn't exist, it creates one.
    qty_change > 0 for Purchases
    qty_change < 0 for Sales
    """
    existing = get_inventory_by_material_and_location(material_id, location_id)
    if existing:
        adjust_inventory(existing["inventory_id"], qty_change)
    else:
        initial_qty = max(0.0, qty_change)
        create_inventory(material_id, location_id, initial_qty)

def upsert_inventory(material_id: int, location_id: int, stock_qty_delta: float) -> Dict[str, Any]:
    # Force conversion to float to prevent string concatenation or improper zero rounding
    qty_change = float(stock_qty_delta)
    logger.debug("inventory.upsert_inventory params=%s", (material_id, location_id, qty_change))
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query(
                "upsert_inventory",
                QUERIES["upsert_inventory"],
                (int(material_id), int(location_id), qty_change),
                cur,
            )
            result = cur.fetchone()
        conn.commit()
    return dict(result) if result else {}
