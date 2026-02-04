CREATE TABLE IF NOT EXISTS procurement.supplier_quotations (
  rfq_id STRING,
  supplier_id STRING,
  price INT64,
  delivery_days INT64,
  payment_terms STRING,
  gcs_uri STRING,
  ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
