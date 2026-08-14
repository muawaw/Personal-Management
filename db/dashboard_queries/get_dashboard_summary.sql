-- db/dashboard_queries/get_dashboard_summary.sql
WITH purchase_agg AS (
    SELECT
        COALESCE(SUM(p.quantity), 0) AS total_purchased_qty,
        COALESCE(SUM(p.total_amount), 0) AS total_purchased_amount,
        CASE WHEN SUM(p.quantity) = 0 THEN NULL ELSE SUM(p.total_amount) / SUM(p.quantity) END AS avg_purchase_price
    FROM purchasing p
    JOIN material m ON p.material_id = m.material_id
    WHERE
        (%s::date IS NULL OR p.purchase_date >= %s::date)
        AND (%s::date IS NULL OR p.purchase_date <= %s::date)
        AND (%s::integer IS NULL OR m.category_id = %s::integer)
        AND (%s::integer IS NULL OR p.material_id = %s::integer)
        AND (%s::integer IS NULL OR p.location_id = %s::integer)
),

sales_agg AS (
    SELECT
        COALESCE(SUM(s.quantity), 0) AS total_sold_qty,
        COALESCE(SUM(s.total_amount), 0) AS total_sales_amount,
        CASE WHEN SUM(s.quantity) = 0 THEN NULL ELSE SUM(s.total_amount) / SUM(s.quantity) END AS avg_sales_price
    FROM sales s
    JOIN material m ON s.material_id = m.material_id
    WHERE
        (%s::date IS NULL OR s.sales_date >= %s::date)
        AND (%s::date IS NULL OR s.sales_date <= %s::date)
        AND (%s::integer IS NULL OR m.category_id = %s::integer)
        AND (%s::integer IS NULL OR s.material_id = %s::integer)
        AND (%s::integer IS NULL OR s.location_id = %s::integer)
),

stock_agg AS (
    SELECT 
        COALESCE(SUM(st.stock_qty), 0) AS total_inventory_qty
    FROM inventory st
    JOIN material m ON st.material_id = m.material_id
    WHERE 
        (%s::date IS NULL OR st.created_at >= %s::date)
        AND (%s::date IS NULL OR st.created_at <= %s::date)
        AND (%s::integer IS NULL OR m.category_id = %s::integer)
        AND (%s::integer IS NULL OR st.material_id = %s::integer)
        AND (%s::integer IS NULL OR st.location_id = %s::integer)
)

SELECT
    p.total_purchased_qty,
    p.total_purchased_amount,
    p.avg_purchase_price,
    s.total_sold_qty,
    s.total_sales_amount,
    s.avg_sales_price,
    st.total_inventory_qty,
    CASE
        WHEN s.total_sold_qty = 0 THEN NULL
        ELSE p.total_purchased_amount / s.total_sold_qty
    END AS purchase_cost_per_sold_unit,
    CASE
        WHEN s.total_sales_amount = 0 THEN NULL
        ELSE s.total_sales_amount - p.total_purchased_amount
    END AS total_margin_amount,
    CASE
        WHEN s.total_sales_amount = 0 THEN NULL
        ELSE (s.total_sales_amount - p.total_purchased_amount) / s.total_sales_amount
    END AS margin_percentage
FROM purchase_agg p
CROSS JOIN sales_agg s
CROSS JOIN stock_agg st;