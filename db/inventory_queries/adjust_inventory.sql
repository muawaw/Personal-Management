UPDATE inventory
SET stock_qty = stock_qty + %s,
    updated_at = CURRENT_TIMESTAMP
WHERE inventory_id = %s
RETURNING inventory_id, material_id, location_id, stock_qty, created_at, updated_at;
