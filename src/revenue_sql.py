# Daily revenue with order-level discount counted ONCE per order
# (discount is kept only on the first item row of each order).
DAILY_REVENUE_SQL = """
    SELECT order_date AS ds, SUM(gross) - SUM(disc) AS y
    FROM (
        SELECT order_date,
               unit_price * quantity AS gross,
               CASE WHEN ROW_NUMBER() OVER (
                        PARTITION BY order_id ORDER BY item_id) = 1
                    THEN discount ELSE 0 END AS disc
        FROM sales
        WHERE is_sale = 1 AND is_outlier = 0
    )
    GROUP BY order_date ORDER BY order_date
"""