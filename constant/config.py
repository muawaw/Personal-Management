import os
from pathlib import Path

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


def get_db_connection():
    from constant.error_handling import connect_db

    return connect_db(DB_URI)


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
