WITH first_purchase AS (
  SELECT
    customer_id,
    MIN(DATE_TRUNC('month', order_purchase_timestamp)) AS cohort_month
  FROM orders
  WHERE order_status = 'delivered'
  GROUP BY 1
),
activity AS (
  SELECT
    o.customer_id,
    fp.cohort_month,
    DATE_TRUNC('month', o.order_purchase_timestamp) AS order_month
  FROM orders o
  JOIN first_purchase fp USING (customer_id)
  WHERE o.order_status = 'delivered'
),
cohort_counts AS (
  SELECT
    cohort_month,
    order_month,
    COUNT(DISTINCT customer_id) AS active_customers
  FROM activity
  GROUP BY 1,2
),
cohort_size AS (
  SELECT cohort_month, MAX(active_customers) AS cohort_customers
  FROM cohort_counts
  GROUP BY 1
)
SELECT
  c.cohort_month,
  c.order_month,
  (EXTRACT(YEAR FROM c.order_month) - EXTRACT(YEAR FROM c.cohort_month)) * 12
  + (EXTRACT(MONTH FROM c.order_month) - EXTRACT(MONTH FROM c.cohort_month)) AS month_index,
  c.active_customers,
  ROUND(100.0 * c.active_customers / NULLIF(s.cohort_customers,0), 2) AS retention_pct
FROM cohort_counts c
JOIN cohort_size s USING (cohort_month)
ORDER BY 1, 3;

WITH first_purchase AS (
  SELECT customer_id, MIN(DATE_TRUNC('month', order_purchase_timestamp)) AS cohort_month
  FROM orders WHERE order_status='delivered'
  GROUP BY 1
),
activity AS (
  SELECT o.customer_id, fp.cohort_month, DATE_TRUNC('month', o.order_purchase_timestamp) AS order_month
  FROM orders o JOIN first_purchase fp USING (customer_id)
  WHERE o.order_status='delivered'
)
SELECT cohort_month, order_month, COUNT(DISTINCT customer_id) AS active_customers
FROM activity
GROUP BY 1,2
ORDER BY 1,2
LIMIT 20;
