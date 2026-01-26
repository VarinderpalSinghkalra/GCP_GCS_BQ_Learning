from google.cloud import documentai_v1 as documentai
from google.cloud import bigquery
from google.cloud import storage
from datetime import datetime
import config


def process_document(event, context):
    file_name = event["name"]
    bucket_name = event["bucket"]

    if not file_name.lower().endswith(".pdf"):
        print(f"Skipping non-PDF file: {file_name}")
        return

    print("🔥 FUNCTION TRIGGERED")
    print(f"Bucket: {bucket_name}")
    print(f"File: {file_name}")

    # Clients
    docai_client = documentai.DocumentProcessorServiceClient()
    bq_client = bigquery.Client()
    storage_client = storage.Client()

    # Download PDF from GCS
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    pdf_bytes = blob.download_as_bytes()
    print(f"📥 Downloaded {len(pdf_bytes)} bytes")

    # Document AI processor path (PROJECT NUMBER)
    processor_name = docai_client.processor_path(
        config.PROJECT_NUMBER,
        config.LOCATION,
        config.PROCESSOR_ID
    )

    # Document AI request
    request = documentai.ProcessRequest(
        name=processor_name,
        raw_document=documentai.RawDocument(
            content=pdf_bytes,
            mime_type="application/pdf"
        )
    )

    result = docai_client.process_document(request=request)
    document = result.document

    rows = []

    # Extract Form Parser fields
    for page in document.pages:
        for field in page.form_fields:
            field_name = (
                field.field_name.text_anchor.content.strip()
                if field.field_name and field.field_name.text_anchor
                else ""
            )
            field_value = (
                field.field_value.text_anchor.content.strip()
                if field.field_value and field.field_value.text_anchor
                else ""
            )

            # Safe confidence
            confidence = 0.0
            if field.field_name and field.field_name.confidence:
                confidence = field.field_name.confidence
            if field.field_value and field.field_value.confidence:
                confidence = max(confidence, field.field_value.confidence)

            rows.append({
                "document_name": file_name,
                "field_name": field_name,
                "field_value": field_value,
                "confidence": confidence,
                "page_number": page.page_number,
                # ✅ FIX: datetime → string
                "processed_at": datetime.utcnow().isoformat()
            })

    # Handle empty form case
    if not rows:
        print("⚠️ No form fields found — inserting fallback row")
        rows.append({
            "document_name": file_name,
            "field_name": "NO_DATA_EXTRACTED",
            "field_value": "Manual review required",
            "confidence": 0.0,
            "page_number": 1,
            "processed_at": datetime.utcnow().isoformat()
        })

    table_id = f"{config.BQ_PROJECT_ID}.{config.BQ_DATASET}.{config.BQ_TABLE}"
    print(f"📌 Writing to BigQuery: {table_id}")
    print(f"🧾 Rows count: {len(rows)}")

    errors = bq_client.insert_rows_json(table_id, rows)

    if errors:
        print("❌ BigQuery insert FAILED")
        for e in errors:
            print(e)
    else:
        print(f"✅ BigQuery insert SUCCESS ({len(rows)} rows)")

