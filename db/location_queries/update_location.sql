UPDATE location
SET location_code = %s,
    location_name = %s,
    description = %s
WHERE location_id = %s
RETURNING location_id, location_code, location_name, description, created_at, updated_at;
