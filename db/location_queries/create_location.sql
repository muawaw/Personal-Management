INSERT INTO location (location_code, location_name, description)
VALUES (%s, %s, %s)
RETURNING location_id, location_code, location_name, description, created_at, updated_at;
