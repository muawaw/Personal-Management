from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional

from constant.config import (
    CATEGORY_QUERIES_DIR,
    LOCATION_QUERIES_DIR,
    MATERIAL_QUERIES_DIR,
    get_db_connection,
    load_sql_queries_from_directories,
)
from constant.error_handling import execute_query
from constant.logger import logger
from constant.error_handling import execute_query


# Cache queries on startup
QUERIES = load_sql_queries_from_directories(
    [CATEGORY_QUERIES_DIR, LOCATION_QUERIES_DIR, MATERIAL_QUERIES_DIR]
)


# ==========================================
# 1. CATEGORY LOGIC
# ==========================================


def create_category(category_code: str, category_name: str) -> Dict[str, Any]:
    logger.debug("master_data.create_category params=%s", (category_code, category_name))
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("create_category", QUERIES["create_category"], (category_code, category_name), cur)
            result = cur.fetchone()
        conn.commit()
    return dict(result)


def get_all_categories() -> List[Dict[str, Any]]:
    logger.debug("master_data.get_all_categories")
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("get_all_categories", QUERIES["get_all_categories"], None, cur)
            result = cur.fetchall()
    return [dict(row) for row in result]


def get_category_by_id(category_id: int) -> Optional[Dict[str, Any]]:
    logger.debug("master_data.get_category_by_id params=%s", (category_id,))
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("get_category_by_id", QUERIES["get_category_by_id"], (category_id,), cur)
            result = cur.fetchone()
    return dict(result) if result else None


def update_category(category_id: int, category_code: str, category_name: str) -> Optional[Dict[str, Any]]:
    logger.debug(
        "master_data.update_category params=%s",
        (category_id, category_code, category_name),
    )
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("update_category", QUERIES["update_category"], (category_code, category_name, category_id), cur)
            result = cur.fetchone()
        conn.commit()
    return dict(result) if result else None


def delete_category(category_id: int) -> bool:
    logger.debug("master_data.delete_category params=%s", (category_id,))
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_query("delete_category", QUERIES["delete_category"], (category_id,), cur)
            deleted = cur.fetchone()
        conn.commit()
    return bool(deleted)


# ==========================================
# 2. LOCATION LOGIC
# ==========================================


def create_location(location_code: str, location_name: str, description: Optional[str] = None) -> Dict[str, Any]:
    logger.debug("master_data.create_location params=%s", (location_code, location_name, description))
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("create_location", QUERIES["create_location"], (location_code, location_name, description), cur)
            result = cur.fetchone()
        conn.commit()
    return dict(result)


def get_all_locations() -> List[Dict[str, Any]]:
    logger.debug("master_data.get_all_locations")
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("get_all_locations", QUERIES["get_all_locations"], None, cur)
            result = cur.fetchall()
    return [dict(row) for row in result]


def get_location_by_id(location_id: int) -> Optional[Dict[str, Any]]:
    logger.debug("master_data.get_location_by_id params=%s", (location_id,))
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("get_location_by_id", QUERIES["get_location_by_id"], (location_id,), cur)
            result = cur.fetchone()
    return dict(result) if result else None


def update_location(location_id: int, location_code: str, location_name: str, description: Optional[str] = None) -> Optional[Dict[str, Any]]:
    logger.debug(
        "master_data.update_location params=%s",
        (location_id, location_code, location_name, description),
    )
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("update_location", QUERIES["update_location"], (location_code, location_name, description, location_id), cur)
            result = cur.fetchone()
        conn.commit()
    return dict(result) if result else None


def delete_location(location_id: int) -> bool:
    logger.debug("master_data.delete_location params=%s", (location_id,))
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_query("delete_location", QUERIES["delete_location"], (location_id,), cur)
            deleted = cur.fetchone()
        conn.commit()
    return bool(deleted)


# ==========================================
# 3. MATERIAL LOGIC
# ==========================================


def create_material(material_code: str, material_name: str, category_id: Optional[int] = None, unit_of_measure: str = "PCS") -> Dict[str, Any]:
    logger.debug(
        "master_data.create_material params=%s",
        (material_code, material_name, category_id, unit_of_measure),
    )
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("create_material", QUERIES["create_material"], (material_code, material_name, category_id, unit_of_measure), cur)
            result = cur.fetchone()
        conn.commit()
    return dict(result)


def get_all_materials() -> List[Dict[str, Any]]:
    logger.debug("master_data.get_all_materials")
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("get_all_materials", QUERIES["get_all_materials"], None, cur)
            result = cur.fetchall()
    return [dict(row) for row in result]


def get_material_by_id(material_id: int) -> Optional[Dict[str, Any]]:
    logger.debug("master_data.get_material_by_id params=%s", (material_id,))
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("get_material_by_id", QUERIES["get_material_by_id"], (material_id,), cur)
            result = cur.fetchone()
    return dict(result) if result else None


def update_material(material_id: int, material_code: str, material_name: str, category_id: Optional[int] = None, unit_of_measure: str = "PCS") -> Optional[Dict[str, Any]]:
    logger.debug(
        "master_data.update_material params=%s",
        (material_id, material_code, material_name, category_id, unit_of_measure),
    )
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("update_material", QUERIES["update_material"], (material_code, material_name, category_id, unit_of_measure, material_id), cur)
            result = cur.fetchone()
        conn.commit()
    return dict(result) if result else None


def delete_material(material_id: int) -> bool:
    logger.debug("master_data.delete_material params=%s", (material_id,))
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_query("delete_material", QUERIES["delete_material"], (material_id,), cur)
            deleted = cur.fetchone()
        conn.commit()
    return bool(deleted)
