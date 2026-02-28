DROP TABLE IF EXISTS customers CASCADE;
CREATE TABLE customers (
  customer_id TEXT PRIMARY KEY,
  customer_unique_id TEXT,
  customer_zip_code_prefix TEXT,
  customer_city TEXT,
  customer_state TEXT
);

DROP TABLE IF EXISTS orders CASCADE;
CREATE TABLE orders (
  order_id TEXT PRIMARY KEY,
  customer_id TEXT REFERENCES customers(customer_id),
  order_status TEXT,
  order_purchase_timestamp TIMESTAMP,
  order_approved_at TIMESTAMP,
  order_delivered_carrier_date TIMESTAMP,
  order_delivered_customer_date TIMESTAMP,
  order_estimated_delivery_date TIMESTAMP
);

DROP TABLE IF EXISTS order_items CASCADE;
CREATE TABLE order_items (
  order_id TEXT REFERENCES orders(order_id),
  order_item_id INT,
  product_id TEXT,
  seller_id TEXT,
  shipping_limit_date TIMESTAMP,
  price NUMERIC,
  freight_value NUMERIC,
  PRIMARY KEY (order_id, order_item_id)
);

DROP TABLE IF EXISTS payments CASCADE;
CREATE TABLE payments (
  order_id TEXT REFERENCES orders(order_id),
  payment_sequential INT,
  payment_type TEXT,
  payment_installments INT,
  payment_value NUMERIC,
  PRIMARY KEY (order_id, payment_sequential)
);

DROP TABLE IF EXISTS products CASCADE;
CREATE TABLE products (
  product_id TEXT PRIMARY KEY,
  product_category_name TEXT,
  product_name_lenght INT,
  product_description_lenght INT,
  product_photos_qty INT,
  product_weight_g NUMERIC,
  product_length_cm NUMERIC,
  product_height_cm NUMERIC,
  product_width_cm NUMERIC
);

CREATE TABLE IF NOT EXISTS sellers CASCADE (
  seller_id TEXT PRIMARY KEY,
  seller_zip_code_prefix TEXT,
  seller_city TEXT,
  seller_state TEXT
);

DROP TABLE IF EXISTS reviews CASCADE;
CREATE TABLE reviews (
  review_id TEXT,
  order_id TEXT REFERENCES orders(order_id),
  review_score INT,
  review_comment_title TEXT,
  review_comment_message TEXT,
  review_creation_date TIMESTAMP,
  review_answer_timestamp TIMESTAMP
);

CREATE TABLE IF NOT EXISTS category_translation (
  product_category_name TEXT PRIMARY KEY,
  product_category_name_english TEXT
);