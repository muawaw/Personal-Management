-- name: update_purchase
UPDATE purchasing
SET purchase_number = %s,
    material_id = %s,
    location_id = %s,
    quantity = %s,
    unit_price = %s,
    purchase_date = %s
WHERE purchase_id = %s
RETURNING purchase_id, purchase_number, material_id, location_id, quantity, unit_price, total_amount, purchase_date, created_at, updated_at;
