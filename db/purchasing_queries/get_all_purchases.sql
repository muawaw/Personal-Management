-- name: get_all_purchases
SELECT pu.purchase_id,
       pu.purchase_number,
       pu.material_id,
       m.material_code,
       m.material_name,
       m.unit_of_measure,
       pu.location_id,
       l.location_code,
       l.location_name,
       pu.quantity,
       pu.unit_price,
       pu.total_amount,
       pu.purchase_date,
       pu.created_at,
       pu.updated_at
FROM purchasing pu
JOIN material m ON pu.material_id = m.material_id
JOIN location l ON pu.location_id = l.location_id
ORDER BY pu.purchase_id DESC;
