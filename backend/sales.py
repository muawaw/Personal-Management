from typing import List, Dict, Any, Optional

from psycopg2.extras import RealDictCursor

from constant.config import get_db_connection, load_sql_queries_from_directory, SALES_QUERIES_DIR
from constant.error_handling import execute_query
from constant.logger import logger


# Cache queries on startup
QUERIES = load_sql_queries_from_directory(SALES_QUERIES_DIR)


# ==========================================
# SALES LOGIC
# ==========================================


def create_sale(
    sales_number: str,
    material_id: int,
    location_id: int,
    quantity: float,
    unit_price: float,
    sales_date: str,
) -> Dict[str, Any]:
    logger.debug(
        "sales.create_sale params=%s",
        (sales_number, material_id, location_id, quantity, unit_price, sales_date),
    )
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query(
                "create_sale",
                QUERIES["create_sale"],
                (sales_number, material_id, location_id, quantity, unit_price, sales_date),
                cur,
            )
            result = cur.fetchone()
        conn.commit()
    return dict(result)


def get_all_sales() -> List[Dict[str, Any]]:
    logger.debug("sales.get_all_sales")
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("get_all_sales", QUERIES["get_all_sales"], None, cur)
            result = cur.fetchall()
    return [dict(row) for row in result]


def get_sale_by_id(sale_id: int) -> Optional[Dict[str, Any]]:
    logger.debug("sales.get_sale_by_id params=%s", (sale_id,))
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("get_sale_by_id", QUERIES["get_sale_by_id"], (sale_id,), cur)
            result = cur.fetchone()
    return dict(result) if result else None


def update_sale(
    sale_id: int,
    sales_number: str,
    material_id: int,
    location_id: int,
    quantity: float,
    unit_price: float,
    sales_date: str,
) -> Optional[Dict[str, Any]]:
    logger.debug(
        "sales.update_sale params=%s",
        (sale_id, sales_number, material_id, location_id, quantity, unit_price, sales_date),
    )
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query(
                "update_sale",
                QUERIES["update_sale"],
                (sales_number, material_id, location_id, quantity, unit_price, sales_date, sale_id),
                cur,
            )
            result = cur.fetchone()
        conn.commit()
    return dict(result) if result else None


def delete_sale(sale_id: int) -> bool:
    logger.debug("sales.delete_sale params=%s", (sale_id,))
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_query("delete_sale", QUERIES["delete_sale"], (sale_id,), cur)
            deleted = cur.fetchone()
        conn.commit()
    return bool(deleted)
