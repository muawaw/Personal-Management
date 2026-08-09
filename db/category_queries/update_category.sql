UPDATE category
SET category_code = %s,
    category_name = %s
WHERE category_id = %s
RETURNING category_id, category_code, category_name, created_at, updated_at;
