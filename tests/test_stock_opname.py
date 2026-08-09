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

# Lightweight psycopg2 stub for module import in tests.
psycopg2_stub = types.ModuleType("psycopg2")
psycopg2_stub.connect = lambda *args, **kwargs: None
extras_stub = types.ModuleType("psycopg2.extras")
extras_stub.RealDictCursor = object
sys.modules.setdefault("psycopg2", psycopg2_stub)
sys.modules.setdefault("psycopg2.extras", extras_stub)

from backend import stock_opname


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


class StockOpnameTests(unittest.TestCase):
    def test_create_stock_opname_returns_new_record(self):
        cursor = FakeCursor(fetchone_result={"opname_id": 1, "actual_qty": 100})
        connection = FakeConnection(cursor)

        with patch.object(stock_opname, "get_db_connection", return_value=connection):
            result = stock_opname.create_stock_opname(
                material_id=1,
                location_id=1,
                system_qty=95.0,
                actual_qty=100.0,
                difference_qty=5.0,
                stock_opname_date="2026-08-08",
                notes="Stock count",
            )

        self.assertEqual(result, {"opname_id": 1, "actual_qty": 100})
        self.assertEqual(cursor.executed_queries[0], stock_opname.QUERIES["create_stock_opname"])
        self.assertEqual(
            cursor.executed_params[0],
            (1, 1, 95.0, 100.0, 5.0, "2026-08-08", "Stock count"),
        )
        self.assertTrue(connection.committed)

    def test_get_all_stock_opname_returns_list_of_dicts(self):
        expected_rows = [
            {"opname_id": 1, "actual_qty": 100},
            {"opname_id": 2, "actual_qty": 90},
        ]
        cursor = FakeCursor(fetchall_result=expected_rows)
        connection = FakeConnection(cursor)

        with patch.object(stock_opname, "get_db_connection", return_value=connection):
            result = stock_opname.get_all_stock_opname()

        self.assertEqual(result, expected_rows)
        self.assertEqual(cursor.executed_queries[0], stock_opname.QUERIES["get_all_stock_opname"])

    def test_get_stock_opname_by_id_returns_record(self):
        cursor = FakeCursor(fetchone_result={"opname_id": 1, "actual_qty": 100})
        connection = FakeConnection(cursor)

        with patch.object(stock_opname, "get_db_connection", return_value=connection):
            result = stock_opname.get_stock_opname_by_id(1)

        self.assertEqual(result, {"opname_id": 1, "actual_qty": 100})
        self.assertEqual(cursor.executed_params[0], (1,))

    def test_update_stock_opname_returns_updated_record(self):
        cursor = FakeCursor(fetchone_result={"opname_id": 1, "actual_qty": 105})
        connection = FakeConnection(cursor)

        with patch.object(stock_opname, "get_db_connection", return_value=connection):
            result = stock_opname.update_stock_opname(
                opname_id=1,
                material_id=1,
                location_id=1,
                system_qty=100.0,
                actual_qty=105.0,
                difference_qty=5.0,
                stock_opname_date="2026-08-08",
                notes="Adjust count",
            )

        self.assertEqual(result, {"opname_id": 1, "actual_qty": 105})
        self.assertEqual(
            cursor.executed_params[0],
            (1, 1, 100.0, 105.0, 5.0, "2026-08-08", "Adjust count", 1),
        )
        self.assertTrue(connection.committed)

    # def test_delete_stock_opname_returns_true_when_deleted(self):
    #     cursor = FakeCursor(fetchone_result=(1,))
    #     connection = FakeConnection(cursor)

    #     with patch.object(stock_opname, "get_db_connection", return_value=connection):
    #         deleted = stock_opname.delete_stock_opname(1)

    #     self.assertTrue(deleted)
    #     self.assertEqual(cursor.executed_params[0], (1,))
    #     self.assertTrue(connection.committed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
