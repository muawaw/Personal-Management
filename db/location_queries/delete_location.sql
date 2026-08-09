DELETE FROM location 
WHERE location_id = %s 
RETURNING location_id;
