import psycopg2
from psycopg2 import Error as Psycopg2Error
from typing import Any, Optional

from constant.logger import logger


class DatabaseError(Exception):
    """Base exception for database-layer errors."""


class DatabaseConnectionError(DatabaseError):
    """Raised when the application cannot connect to the database."""


class DatabaseQueryError(DatabaseError):
    """Raised when a SQL query fails during execution."""


def connect_db(db_uri: str):
    try:
        return psycopg2.connect(db_uri)
    except psycopg2.OperationalError as exc:
        logger.error("Database connection failed: %s", exc)
        raise DatabaseConnectionError(f"Database connection failed: {exc}") from exc
    except Psycopg2Error as exc:
        logger.error("Database connection error: %s", exc)
        raise DatabaseError(f"Database connection error: {exc}") from exc


def execute_query(query_name: str, query: str, params: Optional[tuple], cursor: Any) -> None:
    try:
        cursor.execute(query, params)
    except psycopg2.OperationalError as exc:
        logger.error("Operational error while executing query '%s': %s", query_name, exc)
        raise DatabaseConnectionError(
            f"Operational error while executing query '{query_name}': {exc}"
        ) from exc
    except Psycopg2Error as exc:
        logger.error("Query '%s' failed with params %s: %s", query_name, params, exc)
        raise DatabaseQueryError(f"Query '{query_name}' failed: {exc}") from exc
