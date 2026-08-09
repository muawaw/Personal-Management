SELECT m.material_id, m.material_code, m.material_name, m.unit_of_measure,
       m.category_id, c.category_code, c.category_name,
       m.created_at, m.updated_at
FROM material m
LEFT JOIN category c ON m.category_id = c.category_id
ORDER BY m.material_id ASC;
