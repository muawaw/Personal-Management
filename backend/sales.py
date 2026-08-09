from typing import List, Dict, Any, Optional

from psycopg2.extras import RealDictCursor

from constant.config import get_db_connection, load_sql_queries_from_directory, SALES_QUERIES_DIR
from constant.error_handling import execute_query
from constant.logger import logger

from backend.inventory import upsert_inventory, get_inventory_by_material_and_location

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
    qty_val = float(quantity)
    inv = get_inventory_by_material_and_location(material_id, location_id)
    current_stock = float(inv["stock_qty"]) if inv else 0.0

    if current_stock < qty_val:
        raise ValueError(f"Insufficient stock. Current stock is {current_stock:g}, but requested quantity is {qty_val:g}.")

    logger.debug("sales.create_sale params=%s", (sales_number, material_id, location_id, qty_val, unit_price, sales_date))
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

    upsert_inventory(material_id, location_id, -float(quantity))

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
    old_sale = get_sale_by_id(sale_id) 
    qty_val = float(quantity)

    # Calculate effective stock available if updating same material/location
    inv = get_inventory_by_material_and_location(material_id, location_id)
    current_stock = float(inv["stock_qty"]) if inv else 0.0
    if old_sale and old_sale["material_id"] == material_id and old_sale["location_id"] == location_id:
        current_stock += float(old_sale["quantity"])

    if current_stock < qty_val:
        raise ValueError(f"Cannot update sale. Available stock is {current_stock:g}, but requested quantity is {qty_val:g}.")

    if old_sale:
        upsert_inventory(old_sale["material_id"], old_sale["location_id"], float(old_sale["quantity"]))

    logger.debug("sales.update_sale params=%s", (sale_id, sales_number, material_id, location_id, qty_val, unit_price, sales_date))

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

    upsert_inventory(material_id, location_id, -float(quantity))

    return dict(result) if result else None


def delete_sale(sale_id: int) -> bool:
    logger.debug("sales.delete_sale params=%s", (sale_id,))

    old_sale = get_sale_by_id(sale_id)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_query("delete_sale", QUERIES["delete_sale"], (sale_id,), cur)
            deleted = cur.fetchone()
        conn.commit()

    if old_sale:
        upsert_inventory(
            old_sale["material_id"], 
            old_sale["location_id"], 
            float(old_sale["quantity"])
        )

    return bool(deleted)
