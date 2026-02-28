-- Monthly revenue, orders, customers
SELECT
  DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
  COUNT(DISTINCT o.order_id) AS orders,
  COUNT(DISTINCT c.customer_unique_id) AS customers,
  SUM(p.payment_value) AS revenue
FROM orders o
JOIN customers c USING (customer_id)
JOIN payments p USING (order_id)
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY 1;

-- Average order value (AOV) per month
SELECT
  DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
  SUM(p.payment_value) / NULLIF(COUNT(DISTINCT o.order_id),0) AS aov
FROM orders o
JOIN payments p USING (order_id)
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY 1;

-- Repeat customer %
WITH customer_orders AS (
  SELECT
    c.customer_unique_id,
    COUNT(DISTINCT o.order_id) AS n_orders
  FROM orders o
  JOIN customers c USING (customer_id)
  WHERE o.order_status = 'delivered'
  GROUP BY 1
)
SELECT
  ROUND(
    100.0 * SUM(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END) / COUNT(*),
    2
  ) AS repeat_customer_pct
FROM customer_orders;

-- Top categories by revenue (item-level revenue)
SELECT
  COALESCE(ct.product_category_name_english, p.product_category_name) AS category,
  SUM(oi.price) AS item_revenue
FROM order_items oi
JOIN orders o USING (order_id)
JOIN products p USING (product_id)
LEFT JOIN category_translation ct USING (product_category_name)
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY item_revenue DESC
LIMIT 10;

-- Delivery time (days) summary (delivered orders)
SELECT
  ROUND(AVG(EXTRACT(EPOCH FROM (order_delivered_customer_date - order_purchase_timestamp)) / 86400.0), 2) AS avg_delivery_days,
  ROUND(
    PERCENTILE_CONT(0.5) WITHIN GROUP (
      ORDER BY EXTRACT(EPOCH FROM (order_delivered_customer_date - order_purchase_timestamp)) / 86400.0
    ),
    2
  ) AS median_delivery_days
FROM orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL;