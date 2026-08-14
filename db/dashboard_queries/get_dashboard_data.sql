-- db/dashboard_queries/get_dashboard_data.sql
WITH purchase_agg AS (
    SELECT 
        p.material_id,
        COALESCE(SUM(p.quantity), 0) AS total_purchased_qty,
        COALESCE(SUM(p.total_amount), 0) AS total_purchased_amount
    FROM purchasing p
    JOIN material m ON p.material_id = m.material_id
    WHERE 
        (%s::date IS NULL OR p.purchase_date >= %s::date)
        AND (%s::date IS NULL OR p.purchase_date <= %s::date)
        AND (%s::integer IS NULL OR m.category_id = %s::integer)
        AND (%s::integer IS NULL OR p.material_id = %s::integer)
        AND (%s::integer IS NULL OR p.location_id = %s::integer)
    GROUP BY p.material_id
),

sales_agg AS (
    SELECT 
        s.material_id,
        COALESCE(SUM(s.quantity), 0) AS total_sold_qty,
        COALESCE(SUM(s.total_amount), 0) AS total_sales_amount
    FROM sales s
    JOIN material m ON s.material_id = m.material_id
    WHERE 
        (%s::date IS NULL OR s.sales_date >= %s::date)
        AND (%s::date IS NULL OR s.sales_date <= %s::date)
        AND (%s::integer IS NULL OR m.category_id = %s::integer)
        AND (%s::integer IS NULL OR s.material_id = %s::integer)
        AND (%s::integer IS NULL OR s.location_id = %s::integer)
    GROUP BY s.material_id
),

stock_agg AS (
    SELECT 
        st.material_id,
        COALESCE(SUM(st.stock_qty), 0) AS total_inventory_qty
    FROM inventory st
    JOIN material m ON st.material_id = m.material_id
    WHERE 
        (%s::date IS NULL OR st.created_at >= %s::date)
        AND (%s::date IS NULL OR st.created_at <= %s::date)
        AND (%s::integer IS NULL OR m.category_id = %s::integer)
        AND (%s::integer IS NULL OR st.material_id = %s::integer)
        AND (%s::integer IS NULL OR st.location_id = %s::integer)
    GROUP BY st.material_id
)

SELECT 
    m.material_id,
    m.material_name,
    COALESCE(p.total_purchased_qty, 0) AS total_purchased_qty,
    COALESCE(p.total_purchased_amount, 0) AS total_purchased_amount,
    COALESCE(s.total_sold_qty, 0) AS total_sold_qty,
    COALESCE(s.total_sales_amount, 0) AS total_sales_amount,
    COALESCE(st.total_inventory_qty, 0) AS total_inventory_qty
FROM material m
LEFT JOIN purchase_agg p ON m.material_id = p.material_id
LEFT JOIN sales_agg s ON m.material_id = s.material_id
LEFT JOIN stock_agg st ON m.material_id = st.material_id
WHERE (%s::integer IS NULL OR m.category_id = %s::integer);