INSERT INTO category (category_code, category_name)
VALUES (%s, %s)
RETURNING category_id, category_code, category_name, created_at, updated_at;