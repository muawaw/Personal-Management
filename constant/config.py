import os
from pathlib import Path
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
import streamlit as st
from typing import Dict, List

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
ENV_PATH = os.path.join(ROOT_DIR, ".env")

if Path(ENV_PATH).exists():
    from dotenv import load_dotenv

    load_dotenv(ENV_PATH)

DB_URI = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/postgres")
DB_DIR = os.path.join(ROOT_DIR, "db")

CATEGORY_QUERIES_DIR = os.path.join(DB_DIR, "category_queries")
LOCATION_QUERIES_DIR = os.path.join(DB_DIR, "location_queries")
MATERIAL_QUERIES_DIR = os.path.join(DB_DIR, "material_queries")
PURCHASING_QUERIES_DIR = os.path.join(DB_DIR, "purchasing_queries")
INVENTORY_QUERIES_DIR = os.path.join(DB_DIR, "inventory_queries")
STOCK_OPNAME_QUERIES_DIR = os.path.join(DB_DIR, "stock_opname_queries")
SALES_QUERIES_DIR = os.path.join(DB_DIR, "sales_queries")
DASHBOARD_QUERIES_DIR = os.path.join(DB_DIR, "dashboard_queries")

@st.cache_resource
def get_connection_pool() -> ThreadedConnectionPool:
    """Initialize a persistent thread-safe connection pool on startup."""
    from constant.logger import logger
    logger.info("Initializing psycopg2 ThreadedConnectionPool...")
    return ThreadedConnectionPool(minconn=1, maxconn=10, dsn=DB_URI)

@contextmanager
def get_db_connection():
    """Context manager that borrows a connection from the pool and returns it automatically."""
    pool = get_connection_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


def load_sql_queries_from_directory(directory: str) -> Dict[str, str]:
    queries: Dict[str, str] = {}

    if not os.path.exists(directory):
        raise FileNotFoundError(f"SQL directory not found: {directory}")

    for file_name in os.listdir(directory):
        if not file_name.endswith(".sql"):
            continue

        query_name = os.path.splitext(file_name)[0]
        file_path = os.path.join(directory, file_name)

        if query_name in queries:
            raise ValueError(f"Duplicate SQL query name found: {query_name}")

        with open(file_path, "r", encoding="utf-8-sig") as f:
            query_text = f.read().strip()

        if not query_text:
            raise ValueError(f"SQL file is empty: {file_path}")

        queries[query_name] = query_text

    return queries


def load_sql_queries_from_directories(directories: List[str]) -> Dict[str, str]:
    queries: Dict[str, str] = {}

    for directory in directories:
        if not os.path.exists(directory):
            raise FileNotFoundError(f"SQL directory not found: {directory}")

        for file_name in os.listdir(directory):
            if not file_name.endswith(".sql"):
                continue

            query_name = os.path.splitext(file_name)[0]
            file_path = os.path.join(directory, file_name)

            if query_name in queries:
                raise ValueError(f"Duplicate SQL query name found: {query_name}")

            with open(file_path, "r", encoding="utf-8-sig") as f:
                query_text = f.read().strip()

            if not query_text:
                raise ValueError(f"SQL file is empty: {file_path}")

            queries[query_name] = query_text

    return queries
