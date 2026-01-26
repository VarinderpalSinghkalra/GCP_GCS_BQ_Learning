
## Automated W-9 Document Processing using Google Cloud & Document AI

---

## 1. Overview

This repository contains a **serverless Proof of Concept (PoC)** that demonstrates automated processing of **IRS W-9 documents** using **Google Cloud Platform**.

The solution automatically ingests documents uploaded to **Google Cloud Storage (GCS)**, extracts structured information using **Google Document AI (Form Parser)**, and stores the extracted insights in **BigQuery** for downstream analytics, compliance checks, and onboarding workflows.

The architecture is **event-driven, scalable, and production-aligned**.

---

## 2. Architecture

```
User / Admin
   │
   │ (Manual or Programmatic Upload)
   ▼
Google Cloud Storage (Input Bucket)
   │
   │ Object Finalize Event
   ▼
Cloud Function (Python)
   │
   ├─ Downloads PDF from GCS
   ├─ Sends document to Document AI
   ├─ Extracts structured form fields
   ▼
Google Document AI (Form Parser)
   │
   ▼
BigQuery (Structured Insights Table)
```

---

## 3. High-Level Workflow

1. A W-9 PDF is uploaded to a designated GCS bucket
2. A Cloud Storage **object finalize event** triggers a Cloud Function
3. The Cloud Function:

   * Downloads the document
   * Sends it to Document AI (Form Parser)
   * Extracts key-value form fields
4. Extracted data is stored in BigQuery
5. If no form data is detected, the document is flagged for **manual review**

---

## 4. Technology Stack

* Google Cloud Storage
* Cloud Functions (Gen 1)
* Google Document AI – Form Parser
* Google BigQuery
* Python 3.10

---

## 5. Repository Structure

```
gcs-docai-bq-w9-poc/
│
├── main.py           # Cloud Function logic
├── config.py         # Configuration (Project, Processor, BigQuery)
├── requirements.txt  # Python dependencies
└── README.md         # Project documentation
```

---

## 6. Prerequisites

* Google Cloud Project with billing enabled
* Enabled APIs:

  * Cloud Functions
  * Cloud Storage
  * Document AI
  * BigQuery
* Installed CLI tools:

  * `gcloud`
  * `gsutil`
  * `bq`

---

## 7. Document AI Configuration

### Processor Setup

1. Navigate to **Document AI** in Google Cloud Console
2. Create a new processor of type **Form Parser**
3. Set region to **us**
4. Enable the processor

### Required Configuration Values

* Project Number
* Processor ID
* Location (us)

These values are referenced in `config.py`.

---

## 8. BigQuery Setup

### Create Dataset

```bash
bq mk document_insights
```

### Create Table

```bash
bq mk document_insights.w9_extracted_data \
document_name:STRING,\
field_name:STRING,\
field_value:STRING,\
confidence:FLOAT,\
page_number:INTEGER,\
processed_at:TIMESTAMP
```

---

## 9. Cloud Storage Setup

Create an input bucket for document uploads:

```bash
gsutil mb gs://doc-input-bucket
```

---

## 10. IAM Configuration

Grant BigQuery write permissions to the Cloud Functions runtime service account:

```bash
gcloud projects add-iam-policy-binding my-big-query-project-479504 \
  --member="serviceAccount:245950264824-compute@developer.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"
```

---

## 11. Deployment

Deploy the Cloud Function (Gen 1):

```bash
gcloud functions deploy process_document \
--no-gen2 \
--runtime python310 \
--region us-central1 \
--trigger-resource doc-input-bucket \
--trigger-event google.storage.object.finalize \
--entry-point process_document
```

---

## 12. Triggering the Pipeline

### Manual Upload (Supported)

Manual uploads via **GCP Console** or **gsutil** automatically trigger the pipeline.

```bash
gsutil cp fw9.pdf gs://doc-input-bucket/fw9_$(date +%s).pdf
```

> Note: Always upload with a **new filename** to ensure the trigger fires.

---

## 13. Monitoring & Logs

### View Cloud Function Logs

```bash
gcloud functions logs read process_document --limit 50
```

Expected log flow:

```
FUNCTION TRIGGERED
Document downloaded from GCS
Form fields extracted
BigQuery insert successful
```

---

## 14. Querying Results

```sql
SELECT
  document_name,
  field_name,
  field_value,
  confidence,
  processed_at
FROM `my-big-query-project-479504.document_insights.w9_extracted_data`
ORDER BY processed_at DESC;
```

---

## 15. Empty / Invalid Document Handling

If no form fields are detected:

* A fallback record is written to BigQuery
* The document is flagged as **manual review required**
* The pipeline does not fail or stop processing

This ensures **operational resilience**.

---

## 16. Key Outcomes

* Fully automated, event-driven document processing
* AI-based form understanding (no rule-based parsing)
* Analytics-ready structured output
* Robust error handling and auditability

---

## 17. Future Enhancements

* Risk classification (LOW / MEDIUM / HIGH)
* Auto-approval workflows
* Support for W-8 and invoice documents
* BigQuery dashboards
* Workflow / notification integration

---

## 18. Conclusion

This PoC demonstrates how **Google Cloud + Document AI** can be leveraged to build **scalable, compliant, and enterprise-grade document processing pipelines** suitable for supplier onboarding, compliance verification, and operational analytics.



Just say the word.
