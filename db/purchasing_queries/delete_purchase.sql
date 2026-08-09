-- name: delete_purchase
DELETE FROM purchasing
WHERE purchase_id = %s
RETURNING purchase_id;
