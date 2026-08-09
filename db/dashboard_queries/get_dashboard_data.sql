WITH purchase_agg AS (
    SELECT
        material_id,
        location_id,
        SUM(quantity) AS total_purchased_qty,
        SUM(total_amount) AS total_purchased_amount,
        CASE WHEN SUM(quantity) = 0 THEN NULL ELSE SUM(total_amount) / SUM(quantity) END AS avg_purchase_price
    FROM purchasing
    WHERE
        (%s::date IS NULL OR purchase_date >= %s::date)
        AND (%s::date IS NULL OR purchase_date <= %s::date)
        AND (%s::integer IS NULL OR material_id = %s::integer)
        AND (%s::integer IS NULL OR location_id = %s::integer)
    GROUP BY material_id, location_id
),

sales_agg AS (
    SELECT
        material_id,
        location_id,
        SUM(quantity) AS total_sold_qty,
        SUM(total_amount) AS total_sales_amount,
        CASE WHEN SUM(quantity) = 0 THEN NULL ELSE SUM(total_amount) / SUM(quantity) END AS avg_sales_price
    FROM sales
    WHERE
        (%s::date IS NULL OR sales_date >= %s::date)
        AND (%s::date IS NULL OR sales_date <= %s::date)
        AND (%s::integer IS NULL OR material_id = %s::integer)
        AND (%s::integer IS NULL OR location_id = %s::integer)
    GROUP BY material_id, location_id
),

stock_agg AS (
    SELECT
        material_id,
        location_id,
        SUM(difference_qty) AS total_stock_difference_qty
    FROM stock_opname
    WHERE
        (%s::date IS NULL OR stock_opname_date >= %s::date)
        AND (%s::date IS NULL OR stock_opname_date <= %s::date)
        AND (%s::integer IS NULL OR material_id = %s::integer)
        AND (%s::integer IS NULL OR location_id = %s::integer)
    GROUP BY material_id, location_id
)
SELECT
    COALESCE(p.material_id, s.material_id, o.material_id) AS material_id,
    m.material_code,
    m.material_name,
    COALESCE(p.location_id, s.location_id, o.location_id) AS location_id,
    l.location_code,
    l.location_name,
    COALESCE(p.total_purchased_qty, 0) AS total_purchased_qty,
    COALESCE(p.total_purchased_amount, 0) AS total_purchased_amount,
    p.avg_purchase_price,
    COALESCE(s.total_sold_qty, 0) AS total_sold_qty,
    COALESCE(s.total_sales_amount, 0) AS total_sales_amount,
    s.avg_sales_price,
    COALESCE(o.total_stock_difference_qty, 0) AS total_stock_difference_qty
FROM purchase_agg p
FULL OUTER JOIN sales_agg s USING (material_id, location_id)
FULL OUTER JOIN stock_agg o USING (material_id, location_id)
JOIN material m ON m.material_id = COALESCE(p.material_id, s.material_id, o.material_id)
LEFT JOIN location l ON l.location_id = COALESCE(p.location_id, s.location_id, o.location_id)
ORDER BY m.material_code, l.location_code;