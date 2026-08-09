INSERT INTO inventory (material_id, location_id, stock_qty)
VALUES (%s, %s, %s)
RETURNING inventory_id, material_id, location_id, stock_qty, created_at, updated_at;
