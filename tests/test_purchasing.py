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

# Provide a lightweight stub for psycopg2 so the module can be imported in a minimal environment.
psycopg2_stub = types.ModuleType("psycopg2")
psycopg2_stub.connect = lambda *args, **kwargs: None
extras_stub = types.ModuleType("psycopg2.extras")
extras_stub.RealDictCursor = object
sys.modules.setdefault("psycopg2", psycopg2_stub)
sys.modules.setdefault("psycopg2.extras", extras_stub)

from backend import purchasing


class FakeCursor:
    def __init__(self, rows=None, *, fetchone_result=None, fetchall_result=None):
        self.rows = rows or []
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


class PurchasingTests(unittest.TestCase):
    def test_load_sql_queries_from_directory_loads_sql_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "create_purchase.sql"), "w", encoding="utf-8") as handle:
                handle.write("INSERT INTO purchases VALUES (1);")
            with open(os.path.join(temp_dir, "get_all_purchases.sql"), "w", encoding="utf-8") as handle:
                handle.write("SELECT * FROM purchases;")

            queries = purchasing.load_sql_queries_from_directory(temp_dir)

            self.assertEqual(
                queries["create_purchase"],
                "INSERT INTO purchases VALUES (1);",
                "The create_purchase SQL query should be loaded from the SQL file.",
            )
            self.assertEqual(
                queries["get_all_purchases"],
                "SELECT * FROM purchases;",
                "The get_all_purchases SQL query should be loaded from the SQL file.",
            )
            self.assertEqual(
                set(queries.keys()),
                {"create_purchase", "get_all_purchases"},
                "The SQL loader should return exactly the expected query names.",
            )

    def test_load_sql_queries_from_directory_strips_utf8_bom(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "create_purchase.sql"), "w", encoding="utf-8-sig") as handle:
                handle.write("INSERT INTO purchases VALUES (1);")

            queries = purchasing.load_sql_queries_from_directory(temp_dir)

            self.assertEqual(
                queries["create_purchase"],
                "INSERT INTO purchases VALUES (1);",
                "The SQL loader should remove a UTF-8 BOM from SQL file contents.",
            )

    def test_create_purchase_executes_query_and_returns_row(self):
        cursor = FakeCursor(fetchone_result={"id": 10, "purchase_number": "PO-100"})
        connection = FakeConnection(cursor)

        with patch.object(purchasing, "get_db_connection", return_value=connection):
            result = purchasing.create_purchase(
                purchase_number="PO-100",
                material_id=1,
                location_id=2,
                quantity=5,
                unit_price=100.0,
                purchase_date=None,
            )

        self.assertEqual(
            result,
            {"id": 10, "purchase_number": "PO-100"},
            "create_purchase should return the inserted purchase row.",
        )
        self.assertEqual(len(cursor.executed_queries), 1, "create_purchase should execute exactly one SQL statement.")
        self.assertEqual(
            cursor.executed_queries[0],
            purchasing.QUERIES["create_purchase"],
            "create_purchase should use the SQL query loaded from the SQL file.",
        )
        self.assertEqual(
            cursor.executed_params[0][0:5],
            ("PO-100", 1, 2, 5, 100.0),
            "create_purchase should pass the purchase input values to the query.",
        )
        self.assertEqual(
            cursor.executed_params[0][5].__class__.__name__,
            "date",
            "create_purchase should convert the purchase_date to a date object.",
        )
        self.assertTrue(connection.committed, "create_purchase should commit the transaction.")

    def test_get_all_purchases_returns_list_of_dicts(self):
        expected_rows = [{"id": 1, "purchase_number": "PO-1"}, {"id": 2, "purchase_number": "PO-2"}]
        cursor = FakeCursor(fetchall_result=expected_rows)
        connection = FakeConnection(cursor)

        with patch.object(purchasing, "get_db_connection", return_value=connection):
            result = purchasing.get_all_purchases()

        self.assertEqual(result, expected_rows, "get_all_purchases should return all rows from the database.")
        self.assertEqual(
            cursor.executed_queries[0],
            purchasing.QUERIES["get_all_purchases"],
            "get_all_purchases should use the SQL query loaded from the SQL file.",
        )

    def test_get_purchase_by_id_returns_row_or_none(self):
        cursor = FakeCursor(fetchone_result={"id": 3, "purchase_number": "PO-3"})
        connection = FakeConnection(cursor)

        with patch.object(purchasing, "get_db_connection", return_value=connection):
            result = purchasing.get_purchase_by_id(3)

        self.assertEqual(result, {"id": 3, "purchase_number": "PO-3"}, "get_purchase_by_id should return the matching purchase row.")
        self.assertEqual(cursor.executed_params[0], (3,), "get_purchase_by_id should pass the purchase ID as a single parameter.")

    def test_update_purchase_returns_updated_row(self):
        cursor = FakeCursor(fetchone_result={"id": 4, "purchase_number": "PO-4"})
        connection = FakeConnection(cursor)

        with patch.object(purchasing, "get_db_connection", return_value=connection):
            result = purchasing.update_purchase(
                purchase_id=4,
                purchase_number="PO-4",
                material_id=6,
                location_id=7,
                quantity=8,
                unit_price=9.5,
                purchase_date="2024-01-01",
            )

        self.assertEqual(result, {"id": 4, "purchase_number": "PO-4"}, "update_purchase should return the updated purchase row.")
        self.assertEqual(
            cursor.executed_params[0][0:6],
            ("PO-4", 6, 7, 8, 9.5, "2024-01-01"),
            "update_purchase should pass the updated purchase values to the query.",
        )
        self.assertEqual(cursor.executed_params[0][6], 4, "update_purchase should include the purchase ID as the last parameter.")
        self.assertTrue(connection.committed, "update_purchase should commit the transaction.")

    # def test_delete_purchase_returns_true_when_deleted(self):
    #     cursor = FakeCursor(fetchone_result=(1,))
    #     connection = FakeConnection(cursor)

    #     with patch.object(purchasing, "get_db_connection", return_value=connection):
    #         deleted = purchasing.delete_purchase(99)

    #     self.assertTrue(deleted, "delete_purchase should return True when a row is deleted.")
    #     self.assertEqual(cursor.executed_params[0], (99,), "delete_purchase should pass the purchase ID to the query.")
    #     self.assertTrue(connection.committed, "delete_purchase should commit the transaction.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
