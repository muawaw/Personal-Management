DELETE FROM category 
WHERE category_id = %s 
RETURNING category_id;
