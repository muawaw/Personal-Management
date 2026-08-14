import psycopg2
from psycopg2 import Error as Psycopg2Error
from typing import Any, Optional, Callable
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from constant.logger import logger


class DatabaseError(Exception):
    """Base exception for database-layer errors."""


class DatabaseConnectionError(DatabaseError):
    """Raised when the application cannot connect to the database."""


class DatabaseQueryError(DatabaseError):
    """Raised when a SQL query fails during execution."""


def connect_db(db_uri: str):
    """Establishes a connection to PostgreSQL with cloud SSL & timeout enforcement."""
    try:
        # Enforce sslmode=require and set a connection timeout for cloud DBs
        parsed_url = urlparse(db_uri)
        query_params = parse_qs(parsed_url.query)
        
        if "sslmode" not in query_params:
            query_params["sslmode"] = ["require"]
        if "connect_timeout" not in query_params:
            query_params["connect_timeout"] = ["10"]
            
        updated_query = urlencode(query_params, doseq=True)
        updated_url_parts = list(parsed_url)
        updated_url_parts[4] = updated_query
        target_uri = urlunparse(updated_url_parts)

        return psycopg2.connect(target_uri)
        
    except psycopg2.OperationalError as exc:
        logger.error("Database connection failed: %s", exc)
        raise DatabaseConnectionError("Database connection failed") from exc
    except Psycopg2Error as exc:
        logger.error("Database connection error: %s", exc)
        raise DatabaseError("Database connection error") from exc


def execute_query(
    query_name: str, 
    query: str, 
    params: Optional[tuple], 
    cursor: Any, 
    conn: Optional[Any] = None, 
    db_uri: Optional[str] = None
) -> None:
    """Executes a query with automatic retry if the idle connection socket was dropped."""
    try:
        cursor.execute(query, params)
    except psycopg2.OperationalError as exc:
        # Check if the connection dropped/closed due to idle timeout
        logger.warning("Operational error on query '%s'. Attempting connection recovery...", query_name)
        
        # If connection and URI are passed, attempt a fresh reconnect & retry once
        if conn is not None and db_uri is not None:
            try:
                if not conn.closed:
                    conn.close()
                new_conn = connect_db(db_uri)
                new_cursor = new_conn.cursor()
                new_cursor.execute(query, params)
                logger.info("Successfully recovered connection for query '%s'", query_name)
                return
            except Exception as retry_exc:
                logger.error("Retry failed for query '%s': %s", query_name, retry_exc)

        logger.error("Operational error executing query '%s': %s", query_name, exc)
        raise DatabaseConnectionError(
            f"Operational database error on operation: {query_name}"
        ) from exc
    except Psycopg2Error as exc:
        logger.error("Query '%s' failed with params %s: %s", query_name, params, exc)
        raise DatabaseQueryError(f"Database query error on operation: {query_name}") from exc


def handle_ui_exception(exc: Exception) -> str:
    """Converts internal technical exceptions to clear user-friendly messages."""
    logger.exception("UI Error Encountered: %s", exc)
    
    if isinstance(exc, ValueError):
        return str(exc)
    if isinstance(exc, DatabaseConnectionError):
        return "Unable to connect to the database. Please verify network connection or server status."
    if isinstance(exc, DatabaseQueryError):
        return "A processing error occurred while saving or fetching your data. Please verify your inputs."
    if isinstance(exc, DatabaseError):
        return "Database service encountered an error. Please try again shortly."
        
    return "An unexpected error occurred. Please try again or contact system support."