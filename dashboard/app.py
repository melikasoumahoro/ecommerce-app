import os
import pandas as pd
import streamlit as st
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="E-commerce Analytics Dashboard", layout="wide")
st.title("E-commerce Revenue & Retention Analytics using PostgreSQL")
st.caption("KPIs + cohort retention analysis powered by SQL on Olist dataset.")

# ---- Connection ----
def get_conn():
    # Local default (works on your laptop)
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "ecom_analytics"),
        user=os.getenv("PGUSER", os.getenv("USER", "")),
        password=os.getenv("PGPASSWORD", ""),
    )

@st.cache_data
def run_query(sql: str) -> pd.DataFrame:
    with get_conn() as conn:
        return pd.read_sql_query(sql, conn)

# ---- Queries ----
q_monthly = """
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
"""

q_aov = """
SELECT
  DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
  SUM(p.payment_value) / NULLIF(COUNT(DISTINCT o.order_id),0) AS aov
FROM orders o
JOIN payments p USING (order_id)
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY 1;
"""

q_repeat = """
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
"""

q_top_cats = """
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
"""

q_cohorts = """
WITH first_purchase AS (
  SELECT
    c.customer_unique_id,
    MIN(DATE_TRUNC('month', o.order_purchase_timestamp)) AS cohort_month
  FROM orders o
  JOIN customers c USING (customer_id)
  WHERE o.order_status = 'delivered'
  GROUP BY 1
),
activity AS (
  SELECT
    c.customer_unique_id,
    fp.cohort_month,
    DATE_TRUNC('month', o.order_purchase_timestamp) AS order_month
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN first_purchase fp
    ON c.customer_unique_id = fp.customer_unique_id
  WHERE o.order_status = 'delivered'
),
cohort_counts AS (
  SELECT
    cohort_month,
    order_month,
    COUNT(DISTINCT customer_unique_id) AS active_customers
  FROM activity
  GROUP BY 1,2
),
cohort_size AS (
  SELECT
    cohort_month,
    MAX(active_customers) AS cohort_customers
  FROM cohort_counts
  GROUP BY 1
)
SELECT
  c.cohort_month,
  c.order_month,
  (EXTRACT(YEAR FROM c.order_month) - EXTRACT(YEAR FROM c.cohort_month)) * 12
  + (EXTRACT(MONTH FROM c.order_month) - EXTRACT(MONTH FROM c.cohort_month)) AS month_index,
  c.active_customers,
  ROUND(
    100.0 * c.active_customers / NULLIF(s.cohort_customers,0),
    2
  ) AS retention_pct
FROM cohort_counts c
JOIN cohort_size s USING (cohort_month)
ORDER BY 1,3;
"""

q_30day = """
WITH first_purchase AS (
  SELECT
    c.customer_unique_id,
    MIN(o.order_purchase_timestamp) AS first_purchase
  FROM orders o
  JOIN customers c USING (customer_id)
  WHERE o.order_status = 'delivered'
  GROUP BY 1
),
second_purchase AS (
  SELECT
    fp.customer_unique_id,
    MIN(o.order_purchase_timestamp) AS second_purchase
  FROM first_purchase fp
  JOIN customers c ON c.customer_unique_id = fp.customer_unique_id
  JOIN orders o USING (customer_id)
  WHERE o.order_status = 'delivered'
    AND o.order_purchase_timestamp > fp.first_purchase
  GROUP BY 1
)
SELECT
  ROUND(
    100.0 * COUNT(*) FILTER (
      WHERE second_purchase <= first_purchase + INTERVAL '30 days'
    ) / COUNT(*),
    2
  ) AS retention_30d_pct
FROM first_purchase fp
LEFT JOIN second_purchase sp USING (customer_unique_id);
"""

# ---- Load data ----
monthly = run_query(q_monthly)
aov = run_query(q_aov)
repeat = run_query(q_repeat)
topcats = run_query(q_top_cats)
cohorts = run_query(q_cohorts)
ret30 = run_query(q_30day)

st.metric("30-Day Retention %", f"{ret30.iloc[0,0]:.2f}%")


# ---- KPI Cards ----
total_revenue = float(monthly["revenue"].sum())
total_orders = int(monthly["orders"].sum())
repeat_pct = float(repeat["repeat_customer_pct"].iloc[0])

c1, c2, c3 = st.columns(3)
c1.metric("Total revenue (delivered)", f"{total_revenue:,.0f}")
c2.metric("Total delivered orders", f"{total_orders:,}")
c3.metric("Repeat customer %", f"{repeat_pct:.2f}%")

# ---- Charts ----
left, right = st.columns(2)

with left:
    st.subheader("Revenue over time")
    st.line_chart(monthly.set_index("month")["revenue"])

with right:
    st.subheader("Average order value (AOV)")
    st.line_chart(aov.set_index("month")["aov"])

st.subheader("Top categories by item revenue")
st.dataframe(topcats, use_container_width=True)

# ---- Cohort table ----
st.subheader("Cohort retention (monthly)")
max_months = st.slider("Max months to show", 1, 12, 6)
coh_small = cohorts[cohorts["month_index"] <= max_months].copy()
cohort_sizes = cohorts[cohorts["month_index"] == 0][["cohort_month", "active_customers"]]
large_cohorts = cohort_sizes[cohort_sizes["active_customers"] >= 50]["cohort_month"]

coh_small = coh_small[coh_small["cohort_month"].isin(large_cohorts)]



pivot = coh_small.pivot_table(
    index="cohort_month",
    columns="month_index",
    values="retention_pct",
    aggfunc="mean"
).sort_index()
pivot.index = pivot.index.strftime("%Y-%m")
pivot.columns = pivot.columns.astype(int)
st.dataframe(pivot.fillna(""), use_container_width=True)
st.caption("Rows = cohort start month, columns = months since first purchase, values = retention %.")

st.subheader("Cohort Retention Heatmap")

fig, ax = plt.subplots(figsize=(10,6))
sns.heatmap(
    pivot,
    annot=True,
    fmt=".1f",
    cmap="Blues",
    vmin=0,
    vmax=20,   # cap at 20% to improve visibility
    cbar_kws={'label': 'Retention %'},
    ax=ax
)

ax.set_ylabel("Cohort Month")
ax.set_xlabel("Months Since First Purchase")

st.pyplot(fig)
