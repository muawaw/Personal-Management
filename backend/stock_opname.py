from typing import List, Dict, Any, Optional
from psycopg2.extras import RealDictCursor

from constant.config import get_db_connection, load_sql_queries_from_directory, STOCK_OPNAME_QUERIES_DIR
from constant.error_handling import execute_query
from constant.logger import logger
from backend.inventory import upsert_inventory, get_inventory_by_material_and_location


QUERIES = load_sql_queries_from_directory(STOCK_OPNAME_QUERIES_DIR)


def create_stock_opname(
    material_id: int,
    location_id: int,
    system_qty: float,
    actual_qty: float,
    difference_qty: float,
    stock_opname_date: str,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    logger.debug(
        "stock_opname.create_stock_opname params=%s",
        (material_id, location_id, system_qty, actual_qty, difference_qty, stock_opname_date, notes),
    )
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query(
                "create_stock_opname",
                QUERIES["create_stock_opname"],
                (material_id, location_id, system_qty, actual_qty, difference_qty, stock_opname_date, notes),
                cur,
            )
            result = cur.fetchone()
        conn.commit()

    if result:
        # Adjustment delta to set inventory stock exact to actual_qty
        delta = float(actual_qty) - float(system_qty)
        upsert_inventory(material_id, location_id, delta)

    return dict(result) if result else {}


def get_all_stock_opname() -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("get_all_stock_opname", QUERIES["get_all_stock_opname"], None, cur)
            result = cur.fetchall()
    return [dict(row) for row in result]


def get_stock_opname_by_id(opname_id: int) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("get_stock_opname_by_id", QUERIES["get_stock_opname_by_id"], (opname_id,), cur)
            result = cur.fetchone()
    return dict(result) if result else None


def update_stock_opname(
    opname_id: int,
    material_id: int,
    location_id: int,
    system_qty: float,
    actual_qty: float,
    difference_qty: float,
    stock_opname_date: str,
    notes: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    logger.debug(
        "stock_opname.update_stock_opname params=%s",
        (opname_id, material_id, location_id, system_qty, actual_qty, difference_qty, stock_opname_date, notes),
    )
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query(
                "update_stock_opname",
                QUERIES["update_stock_opname"],
                (material_id, location_id, system_qty, actual_qty, difference_qty, stock_opname_date, notes, opname_id),
                cur,
            )
            result = cur.fetchone()
        conn.commit()

    if result:
        # Re-sync current inventory level to match updated actual_qty
        inv = get_inventory_by_material_and_location(material_id, location_id)
        current_inv_stock = float(inv["stock_qty"]) if inv else 0.0
        delta = float(actual_qty) - current_inv_stock
        upsert_inventory(material_id, location_id, delta)

    return dict(result) if result else None


def delete_stock_opname(opname_id: int) -> bool:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_query("delete_stock_opname", QUERIES["delete_stock_opname"], (opname_id,), cur)
            deleted = cur.fetchone()
        conn.commit()
    return bool(deleted)