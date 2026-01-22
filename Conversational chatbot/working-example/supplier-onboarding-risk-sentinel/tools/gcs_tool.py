from google.cloud import storage

BUCKET_NAME = "contracts-demo-277069041958"

client = storage.Client()

def upload_approved_document(
    supplier_id: str,
    document_type: str,
    file_bytes: bytes,
    filename: str
) -> str | None:
    """
    Uploads approved document to GCS.
    NEVER raises exception (safe for CF).
    """

    try:
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{supplier_id}/{document_type}/{filename}")
        blob.upload_from_string(file_bytes, content_type="application/pdf")
        return f"gs://{BUCKET_NAME}/{blob.name}"

    except Exception as e:
        # Log and continue onboarding
        print(f"[WARN] GCS upload failed: {e}")
        return None

