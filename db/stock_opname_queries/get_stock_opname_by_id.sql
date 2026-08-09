SELECT opname_id, material_id, location_id, system_qty, actual_qty, difference_qty, stock_opname_date, notes, created_at, updated_at
FROM stock_opname
WHERE opname_id = %s;
