import re
from google.cloud import bigquery
from google.cloud import storage

# -------------------------------
# CONFIG
# -------------------------------
BQ_DATASET = "conversational_demo"
BQ_TABLE = "supplier_quotations"

bq_client = bigquery.Client()
storage_client = storage.Client()


def _extract(pattern: str, text: str, cast=str):
    match = re.search(pattern, text)
    return cast(match.group(1)) if match else None


# ✅ ENTRY POINT (MUST be in main.py)
def quotation_gcs_to_bq(event, context):
    bucket_name = event["bucket"]
    object_name = event["name"]

    # Only process quotation emails
    if not object_name.startswith("quotations/") or not object_name.endswith(".eml"):
        print("Skipping non-quotation object:", object_name)
        return

    print(f"Processing quotation: gs://{bucket_name}/{object_name}")

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    email_text = blob.download_as_text()

    # Extract fields
    price = _extract(r"PRICE:\s*(\d+)", email_text, int)
    delivery_days = _extract(r"DELIVERY_DAYS:\s*(\d+)", email_text, int)
    payment_terms = _extract(r"PAYMENT_TERMS:\s*(.+)", email_text)

    # Extract RFQ + supplier from path
    try:
        _, rfq_id, supplier_id, _ = object_name.split("/", 3)
    except ValueError:
        raise RuntimeError(f"Invalid quotation path: {object_name}")

    row = {
        "rfq_id": rfq_id,
        "supplier_id": supplier_id,
        "price": price,
        "delivery_days": delivery_days,
        "payment_terms": payment_terms,
        "gcs_uri": f"gs://{bucket_name}/{object_name}",
    }

    table_id = f"{bq_client.project}.{BQ_DATASET}.{BQ_TABLE}"

    errors = bq_client.insert_rows_json(table_id, [row])
    if errors:
        raise RuntimeError(f"BigQuery insert failed: {errors}")

    print("✅ Quotation inserted into BigQuery:", row)
