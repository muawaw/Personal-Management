DELETE FROM stock_opname
WHERE opname_id = %s
RETURNING opname_id;
