SELECT inventory_id, material_id, location_id, stock_qty, created_at, updated_at
FROM inventory
WHERE material_id = %s AND location_id = %s;