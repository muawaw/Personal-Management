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

from backend import inventory


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


class InventoryTests(unittest.TestCase):
    def test_create_inventory_executes_query_and_returns_row(self):
        cursor = FakeCursor(fetchone_result={"inventory_id": 1, "stock_qty": 20})
        connection = FakeConnection(cursor)

        with patch.object(inventory, "get_db_connection", return_value=connection):
            result = inventory.create_inventory(material_id=1, location_id=1, stock_qty=20.0)

        self.assertEqual(result, {"inventory_id": 1, "stock_qty": 20})
        self.assertEqual(cursor.executed_queries[0], inventory.QUERIES["create_inventory"])
        self.assertEqual(cursor.executed_params[0], (1, 1, 20.0))
        self.assertTrue(connection.committed)

    def test_get_all_inventory_returns_list_of_dicts(self):
        expected_rows = [{"inventory_id": 1, "stock_qty": 20}, {"inventory_id": 2, "stock_qty": 10}]
        cursor = FakeCursor(fetchall_result=expected_rows)
        connection = FakeConnection(cursor)

        with patch.object(inventory, "get_db_connection", return_value=connection):
            result = inventory.get_all_inventory()

        self.assertEqual(result, expected_rows)
        self.assertEqual(cursor.executed_queries[0], inventory.QUERIES["get_all_inventory"])

    def test_get_inventory_by_id_returns_row_or_none(self):
        cursor = FakeCursor(fetchone_result={"inventory_id": 1, "stock_qty": 20})
        connection = FakeConnection(cursor)

        with patch.object(inventory, "get_db_connection", return_value=connection):
            result = inventory.get_inventory_by_id(1)

        self.assertEqual(result, {"inventory_id": 1, "stock_qty": 20})
        self.assertEqual(cursor.executed_params[0], (1,))

    def test_update_inventory_returns_updated_row(self):
        cursor = FakeCursor(fetchone_result={"inventory_id": 1, "stock_qty": 25})
        connection = FakeConnection(cursor)

        with patch.object(inventory, "get_db_connection", return_value=connection):
            result = inventory.update_inventory(inventory_id=1, material_id=1, location_id=1, stock_qty=25.0)

        self.assertEqual(result, {"inventory_id": 1, "stock_qty": 25})
        self.assertEqual(cursor.executed_params[0], (1, 1, 25.0, 1))
        self.assertTrue(connection.committed)

    def test_adjust_inventory_updates_quantity(self):
        cursor = FakeCursor(fetchone_result={"inventory_id": 1, "stock_qty": 30})
        connection = FakeConnection(cursor)

        with patch.object(inventory, "get_db_connection", return_value=connection):
            result = inventory.adjust_inventory(inventory_id=1, quantity_delta=5.0)

        self.assertEqual(result, {"inventory_id": 1, "stock_qty": 30})
        self.assertEqual(cursor.executed_params[0], (5.0, 1))
        self.assertTrue(connection.committed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
