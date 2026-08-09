from calendar import monthrange
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from psycopg2.extras import RealDictCursor

from constant.config import get_db_connection, load_sql_queries_from_directory, DASHBOARD_QUERIES_DIR
from constant.error_handling import execute_query
from constant.logger import logger

# Cache queries on startup
QUERIES = load_sql_queries_from_directory(DASHBOARD_QUERIES_DIR)

DASHBOARD_FILTER_PRESETS = [
    "current_month",
    "previous_month",
    "last_3_months",
    "last_6_months",
    "last_year",
    "all_time",
]

DASHBOARD_PAGE_SIZE_DEFAULT = 50


def _normalize_date(value: Optional[str]) -> Optional[date]:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        raise ValueError(f"Invalid ISO date value: {value}")


def _shift_months(base_date: date, months: int) -> date:
    year = base_date.year + (base_date.month - 1 + months) // 12
    month = (base_date.month - 1 + months) % 12 + 1
    day = min(base_date.day, monthrange(year, month)[1])
    return date(year, month, day)


def get_dashboard_date_filter_range(filter_name: str) -> Dict[str, Optional[str]]:
    today = date.today()
    current_month_start = date(today.year, today.month, 1)

    if filter_name == "current_month":
        return {
            "start_date": current_month_start.isoformat(),
            "end_date": today.isoformat(),
        }

    if filter_name == "previous_month":
        previous_month_end = current_month_start - timedelta(days=1)
        previous_month_start = date(previous_month_end.year, previous_month_end.month, 1)
        return {
            "start_date": previous_month_start.isoformat(),
            "end_date": previous_month_end.isoformat(),
        }

    if filter_name == "last_3_months":
        start_date = _shift_months(current_month_start, -2)
        return {
            "start_date": start_date.isoformat(),
            "end_date": today.isoformat(),
        }

    if filter_name == "last_6_months":
        start_date = _shift_months(current_month_start, -5)
        return {
            "start_date": start_date.isoformat(),
            "end_date": today.isoformat(),
        }

    if filter_name == "last_year":
        start_date = _shift_months(current_month_start, -11)
        return {
            "start_date": start_date.isoformat(),
            "end_date": today.isoformat(),
        }

    if filter_name == "all_time":
        return {"start_date": None, "end_date": None}

    raise ValueError(f"Unknown dashboard filter name: {filter_name}")


def _build_dashboard_query_params(
    start_date: Optional[date],
    end_date: Optional[date],
    material_id: Optional[int],
    location_id: Optional[int],
) -> tuple[Any, ...]:
    return tuple(
        [start_date, start_date, start_date, start_date]
        + [end_date, end_date, end_date, end_date]
        + [material_id, material_id, material_id, material_id]
        + [location_id, location_id, location_id, location_id]
    )


def get_dashboard_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    material_id: Optional[int] = None,
    location_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Return dashboard aggregates filtered by date, material, and location."""
    normalized_start_date = _normalize_date(start_date)
    normalized_end_date = _normalize_date(end_date)

    logger.debug(
        "dashboard.get_dashboard_data params=%s",
        (normalized_start_date, normalized_end_date, material_id, location_id),
    )

    params = _build_dashboard_query_params(
        normalized_start_date,
        normalized_end_date,
        material_id,
        location_id,
    )

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("get_dashboard_data", QUERIES["get_dashboard_data"], params, cur)
            rows = cur.fetchall()

    return [dict(row) for row in rows]


def get_dashboard_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    material_id: Optional[int] = None,
    location_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Return a dashboard summary row with totals and margin estimations."""
    normalized_start_date = _normalize_date(start_date)
    normalized_end_date = _normalize_date(end_date)

    logger.debug(
        "dashboard.get_dashboard_summary params=%s",
        (normalized_start_date, normalized_end_date, material_id, location_id),
    )

    params = _build_dashboard_query_params(
        normalized_start_date,
        normalized_end_date,
        material_id,
        location_id,
    )

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query("get_dashboard_summary", QUERIES["get_dashboard_summary"], params, cur)
            result = cur.fetchone()

    return dict(result) if result else {}


def get_dashboard_data_paginated(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    material_id: Optional[int] = None,
    location_id: Optional[int] = None,
    page: int = 1,
    page_size: int = DASHBOARD_PAGE_SIZE_DEFAULT,
) -> Dict[str, Any]:
    """Return a single page of dashboard aggregation rows."""
    if page < 1:
        raise ValueError("page must be >= 1")
    if page_size < 1:
        raise ValueError("page_size must be >= 1")

    normalized_start_date = _normalize_date(start_date)
    normalized_end_date = _normalize_date(end_date)

    logger.debug(
        "dashboard.get_dashboard_data_paginated params=%s",
        (
            normalized_start_date,
            normalized_end_date,
            material_id,
            location_id,
            page,
            page_size,
        ),
    )

    params = _build_dashboard_query_params(
        normalized_start_date,
        normalized_end_date,
        material_id,
        location_id,
    ) + (page_size, (page - 1) * page_size)

    paginated_query = f"{QUERIES['get_dashboard_data']}\nLIMIT %s OFFSET %s"

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            execute_query(
                "get_dashboard_data_paginated",
                paginated_query,
                params,
                cur,
            )
            rows = cur.fetchall()

    return {
        "page": page,
        "page_size": page_size,
        "rows": [dict(row) for row in rows],
    }
