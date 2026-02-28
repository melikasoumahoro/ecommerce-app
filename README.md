# E-commerce SQL & Dashboard Analytics 

An analytics project using the Olist e-commerce dataset.  
Built a PostgreSQL schema, loaded raw CSVs into relational tables, and created a Streamlit dashboard to monitor revenue KPIs and customer retention cohorts.

## Highlights
- PostgreSQL relational model across **orders, customers, payments, order_items, products**
- KPI reporting: revenue, orders, customers, AOV, top categories
- Cohort retention analysis using **customer_unique_id** 
- Streamlit dashboard with time-series KPIs and cohort retention heatmap

## Result Screenshots
[Dashboard KPIs](results/dashboard_kpis.png)

[Cohort Retention Heatmap](results/cohort_heatmap.png)

## Dataset
- Public dataset: Olist Brazilian E-commerce: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?resource=download
- Raw CSV files are **not committed** to this repository

## Tech Stack
- PostgreSQL
- SQL (joins, aggregations, cohort logic)
- Python (Pandas)
- Streamlit
- Matplotlib / Seaborn

## How to Run Locally

### 1. Start PostgreSQL and create the database
```bash
createdb ecom_analytics
psql ecom_analytics
```
### 2. Create tables
```bash
psql ecom_analytics -f sql/00_schema.sql
```
#### 3. Load CSVs 
```bash
\copy customers FROM 'data/olist_customers_dataset.csv' WITH (FORMAT csv, HEADER true);
\copy orders FROM 'data/olist_orders_dataset.csv' WITH (FORMAT csv, HEADER true);
\copy order_items FROM 'data/olist_order_items_dataset.csv' WITH (FORMAT csv, HEADER true);
\copy payments FROM 'data/olist_order_payments_dataset.csv' WITH (FORMAT csv, HEADER true);
\copy products FROM 'data/olist_products_dataset.csv' WITH (FORMAT csv, HEADER true);
\copy category_translation FROM 'data/product_category_name_translation.csv' WITH (FORMAT csv, HEADER true);
```

#### 4. Run the dashboard
```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```


## Notes on Customer Identity

Olist distinguishes:
* customer_id: order-level identifier
* customer_unique_id: true customer identity across orders

Repeat-rate and cohort retention metrics use customer_unique_id to avoid undercounting repeat purchases.