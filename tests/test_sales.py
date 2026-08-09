import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Lightweight psycopg2 stub for test import compatibility.
psycopg2_stub = types.ModuleType("psycopg2")
psycopg2_stub.connect = lambda *args, **kwargs: None
extras_stub = types.ModuleType("psycopg2.extras")
extras_stub.RealDictCursor = object
sys.modules.setdefault("psycopg2", psycopg2_stub)
sys.modules.setdefault("psycopg2.extras", extras_stub)

from backend import sales


class FakeCursor:
    def __init__(self, fetchone_result=None, fetchall_result=None):
        self.fetchone_result = fetchone_result
        self.fetchall_result = fetchall_result
        self.executed_queries = []
        self.executed_params = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query, params=None):
        self.executed_queries.append(query)
        self.executed_params.append(params)

    def fetchone(self):
        return self.fetchone_result

    def fetchall(self):
        return self.fetchall_result


class FakeConnection:
    def __init__(self, cursor_obj):
        self.cursor_obj = cursor_obj
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self, cursor_factory=None):
        return self.cursor_obj

    def commit(self):
        self.committed = True


class SalesTests(unittest.TestCase):
    def test_load_sql_queries_from_directory_loads_sql_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "create_sale.sql"), "w", encoding="utf-8") as handle:
                handle.write("INSERT INTO sales VALUES (1);")
            with open(os.path.join(temp_dir, "get_all_sales.sql"), "w", encoding="utf-8") as handle:
                handle.write("SELECT * FROM sales;")

            queries = sales.load_sql_queries_from_directory(temp_dir)

            self.assertEqual(
                queries["create_sale"],
                "INSERT INTO sales VALUES (1);",
                "The create_sale SQL query should be loaded from the SQL file.",
            )
            self.assertEqual(
                queries["get_all_sales"],
                "SELECT * FROM sales;",
                "The get_all_sales SQL query should be loaded from the SQL file.",
            )
            self.assertEqual(
                set(queries.keys()),
                {"create_sale", "get_all_sales"},
                "The SQL loader should return exactly the expected query names.",
            )

    def test_load_sql_queries_from_directory_strips_utf8_bom(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "create_sale.sql"), "w", encoding="utf-8-sig") as handle:
                handle.write("INSERT INTO sales VALUES (1);")

            queries = sales.load_sql_queries_from_directory(temp_dir)

            self.assertEqual(
                queries["create_sale"],
                "INSERT INTO sales VALUES (1);",
                "The SQL loader should remove a UTF-8 BOM from SQL file contents.",
            )

    def test_create_sale_executes_query_and_returns_row(self):
        cursor = FakeCursor(fetchone_result={"sale_id": 1, "sales_number": "SO-100"})
        connection = FakeConnection(cursor)

        with patch.object(sales, "get_db_connection", return_value=connection):
            result = sales.create_sale(
                sales_number="SO-100",
                material_id=1,
                location_id=2,
                quantity=5,
                unit_price=100.0,
                sales_date="2026-08-08",
            )

        self.assertEqual(result, {"sale_id": 1, "sales_number": "SO-100"})
        self.assertEqual(cursor.executed_queries[0], sales.QUERIES["create_sale"])
        self.assertEqual(
            cursor.executed_params[0],
            ("SO-100", 1, 2, 5, 100.0, "2026-08-08"),
        )
        self.assertTrue(connection.committed)

    def test_get_all_sales_returns_list_of_dicts(self):
        expected_rows = [
            {"sale_id": 1, "sales_number": "SO-1"},
            {"sale_id": 2, "sales_number": "SO-2"},
        ]
        cursor = FakeCursor(fetchall_result=expected_rows)
        connection = FakeConnection(cursor)

        with patch.object(sales, "get_db_connection", return_value=connection):
            result = sales.get_all_sales()

        self.assertEqual(result, expected_rows)
        self.assertEqual(cursor.executed_queries[0], sales.QUERIES["get_all_sales"])

    def test_get_sale_by_id_returns_record(self):
        cursor = FakeCursor(fetchone_result={"sale_id": 1, "sales_number": "SO-1"})
        connection = FakeConnection(cursor)

        with patch.object(sales, "get_db_connection", return_value=connection):
            result = sales.get_sale_by_id(1)

        self.assertEqual(result, {"sale_id": 1, "sales_number": "SO-1"})
        self.assertEqual(cursor.executed_params[0], (1,))

    def test_update_sale_returns_updated_row(self):
        cursor = FakeCursor(fetchone_result={"sale_id": 1, "sales_number": "SO-1"})
        connection = FakeConnection(cursor)

        with patch.object(sales, "get_db_connection", return_value=connection):
            result = sales.update_sale(
                sale_id=1,
                sales_number="SO-1",
                material_id=1,
                location_id=2,
                quantity=5,
                unit_price=100.0,
                sales_date="2026-08-08",
            )

        self.assertEqual(result, {"sale_id": 1, "sales_number": "SO-1"})
        self.assertEqual(
            cursor.executed_params[0],
            ("SO-1", 1, 2, 5, 100.0, "2026-08-08", 1),
        )
        self.assertTrue(connection.committed)

    # def test_delete_sale_returns_true_when_deleted(self):
    #     cursor = FakeCursor(fetchone_result=(1,))
    #     connection = FakeConnection(cursor)

    #     with patch.object(sales, "get_db_connection", return_value=connection):
    #         deleted = sales.delete_sale(1)

    #     self.assertTrue(deleted)
    #     self.assertEqual(cursor.executed_params[0], (1,))
    #     self.assertTrue(connection.committed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
