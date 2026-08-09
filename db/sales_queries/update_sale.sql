UPDATE sales
SET sales_number = %s,
    material_id = %s,
    location_id = %s,
    quantity = %s,
    unit_price = %s,
    sales_date = %s
WHERE sale_id = %s
RETURNING sale_id, sales_number, material_id, location_id, quantity, unit_price, total_amount, sales_date, created_at, updated_at;
