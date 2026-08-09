UPDATE material
SET material_code = %s,
    material_name = %s,
    category_id = %s,
    unit_of_measure = %s
WHERE material_id = %s
RETURNING material_id, material_code, material_name, category_id, unit_of_measure, created_at, updated_at;
