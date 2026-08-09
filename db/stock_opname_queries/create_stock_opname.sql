INSERT INTO stock_opname (material_id, location_id, system_qty, actual_qty, difference_qty, stock_opname_date, notes)
VALUES (%s, %s, %s, %s, %s, %s, %s)
RETURNING opname_id, material_id, location_id, system_qty, actual_qty, difference_qty, stock_opname_date, notes, created_at, updated_at;
