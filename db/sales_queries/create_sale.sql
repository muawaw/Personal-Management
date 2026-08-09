INSERT INTO sales (sales_number, material_id, location_id, quantity, unit_price, sales_date)
VALUES (%s, %s, %s, %s, %s, %s)
RETURNING sale_id, sales_number, material_id, location_id, quantity, unit_price, total_amount, sales_date, created_at, updated_at;
