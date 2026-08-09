INSERT INTO purchasing (purchase_number, material_id, location_id, quantity, unit_price, purchase_date)
VALUES (%s, %s, %s, %s, %s, %s)
RETURNING purchase_id, purchase_number, material_id, location_id, quantity, unit_price, total_amount, purchase_date, created_at, updated_at;
