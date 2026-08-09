DELETE FROM material 
WHERE material_id = %s 
RETURNING material_id;
