from typing import List, Dict, Any, Optional

from psycopg2.extras import RealDictCursor

from constant.config import get_db_connection, load_sql_queries_from_directory, STOCK_OPNAME_QUERIES_DIR
from constant.error_handling import execute_query
from constant.logger import logger


# Cache queries on startup
QUERIES = load_sql_queries_from_directory(STOCK_OPNAME_QUERIES_DIR)


# ==========================================
# STOCK OPNAME LOGIC
# ==========================================


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
    return dict(result)


def get_all_stock_opname() -> List[Dict[str, Any]]:
    logger.debug("stock_opname.get_all_stock_opname")
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("get_all_stock_opname", QUERIES["get_all_stock_opname"], None, cur)
            result = cur.fetchall()
    return [dict(row) for row in result]


def get_stock_opname_by_id(opname_id: int) -> Optional[Dict[str, Any]]:
    logger.debug("stock_opname.get_stock_opname_by_id params=%s", (opname_id,))
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
    return dict(result) if result else None


def delete_stock_opname(opname_id: int) -> bool:
    logger.debug("stock_opname.delete_stock_opname params=%s", (opname_id,))
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_query("delete_stock_opname", QUERIES["delete_stock_opname"], (opname_id,), cur)
            deleted = cur.fetchone()
        conn.commit()
    return bool(deleted)
