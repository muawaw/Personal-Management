INSERT INTO material (material_code, material_name, category_id, unit_of_measure)
VALUES (%s, %s, %s, %s)
RETURNING material_id, material_code, material_name, category_id, unit_of_measure, created_at, updated_at;
