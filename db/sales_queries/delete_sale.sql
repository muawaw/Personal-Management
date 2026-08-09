DELETE FROM sales
WHERE sale_id = %s
RETURNING sale_id;
