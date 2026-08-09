WITH purchase_agg AS (
    SELECT
        SUM(quantity) AS total_purchased_qty,
        SUM(total_amount) AS total_purchased_amount,
        CASE WHEN SUM(quantity) = 0 THEN NULL ELSE SUM(total_amount) / SUM(quantity) END AS avg_purchase_price
    FROM purchasing
    WHERE
        (%s::date IS NULL OR purchase_date >= %s::date)
        AND (%s::date IS NULL OR purchase_date <= %s::date)
        AND (%s::integer IS NULL OR material_id = %s::integer)
        AND (%s::integer IS NULL OR location_id = %s::integer)
),

sales_agg AS (
    SELECT
        SUM(quantity) AS total_sold_qty,
        SUM(total_amount) AS total_sales_amount,
        CASE WHEN SUM(quantity) = 0 THEN NULL ELSE SUM(total_amount) / SUM(quantity) END AS avg_sales_price
    FROM sales
    WHERE
        (%s::date IS NULL OR sales_date >= %s::date)
        AND (%s::date IS NULL OR sales_date <= %s::date)
        AND (%s::integer IS NULL OR material_id = %s::integer)
        AND (%s::integer IS NULL OR location_id = %s::integer)
),

stock_agg AS (
    SELECT SUM(difference_qty) AS total_stock_difference_qty
    FROM stock_opname
    WHERE
        (%s::date IS NULL OR stock_opname_date >= %s::date)
        AND (%s::date IS NULL OR stock_opname_date <= %s::date)
        AND (%s::integer IS NULL OR material_id = %s::integer)
        AND (%s::integer IS NULL OR location_id = %s::integer)
)
SELECT
    COALESCE(p.total_purchased_qty, 0) AS total_purchased_qty,
    COALESCE(p.total_purchased_amount, 0) AS total_purchased_amount,
    p.avg_purchase_price,
    COALESCE(s.total_sold_qty, 0) AS total_sold_qty,
    COALESCE(s.total_sales_amount, 0) AS total_sales_amount,
    s.avg_sales_price,
    COALESCE(o.total_stock_difference_qty, 0) AS total_stock_difference_qty,
    CASE
        WHEN COALESCE(s.total_sold_qty, 0) = 0 THEN NULL
        ELSE COALESCE(p.total_purchased_amount, 0) / COALESCE(s.total_sold_qty, 0)
    END AS purchase_cost_per_sold_unit,
    CASE
        WHEN COALESCE(s.total_sales_amount, 0) = 0 THEN NULL
        ELSE COALESCE(s.total_sales_amount, 0) - COALESCE(p.total_purchased_amount, 0)
    END AS total_margin_amount,
    CASE
        WHEN COALESCE(s.total_sales_amount, 0) = 0 THEN NULL
        ELSE (COALESCE(s.total_sales_amount, 0) - COALESCE(p.total_purchased_amount, 0)) / COALESCE(s.total_sales_amount, 0)
    END AS margin_percentage
FROM purchase_agg p
CROSS JOIN sales_agg s
CROSS JOIN stock_agg o;