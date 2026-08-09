INSERT INTO inventory (material_id, location_id, stock_qty)
VALUES (%s, %s, %s::numeric)
ON CONFLICT (material_id, location_id) 
DO UPDATE SET 
    stock_qty = inventory.stock_qty + EXCLUDED.stock_qty,
    updated_at = CURRENT_TIMESTAMP
RETURNING inventory_id, material_id, location_id, stock_qty, created_at, updated_at;