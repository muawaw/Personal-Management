UPDATE stock_opname
SET material_id = %s,
    location_id = %s,
    system_qty = %s,
    actual_qty = %s,
    difference_qty = %s,
    stock_opname_date = %s,
    notes = %s,
    updated_at = CURRENT_TIMESTAMP
WHERE opname_id = %s
RETURNING opname_id, material_id, location_id, system_qty, actual_qty, difference_qty, stock_opname_date, notes, created_at, updated_at;
