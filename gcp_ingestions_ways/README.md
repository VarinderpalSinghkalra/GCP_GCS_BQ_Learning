
⸻

Example: On-Prem Oracle → GCS → BigQuery (Python + Cloud Composer)

Step 1: Understand the Business Requirement

Before writing any code, understand what the business wants.

Example:

A hospital stores patient data in an Oracle database located in its own data center. Every night at 1:00 AM, the hospital wants to copy the latest patient records to Google Cloud so analysts can build dashboards in BigQuery.

The pipeline must:

* Read data from Oracle
* Securely transfer it to GCP
* Store it in Cloud Storage
* Load it into BigQuery
* Notify the team if anything fails

This is the business requirement.

⸻

Step 2: Understand the Architecture

+-----------------------------------------------------------+
|                   On-Premises Data Center                 |
|                                                           |
|  Oracle Database                                          |
|       │                                                   |
|       │ SQL Query                                         |
|       ▼                                                   |
|  Python Extraction Script                                 |
+-------│---------------------------------------------------+
        │
        │ Cloud VPN / Dedicated Interconnect
        ▼
+-----------------------------------------------------------+
|                 Google Cloud Platform                     |
|                                                           |
| Cloud Storage (Raw Bucket)                                |
|       │                                                   |
|       ▼                                                   |
| Cloud Composer (Airflow DAG)                              |
|       │                                                   |
|       ▼                                                   |
| BigQuery                                                  |
|       │                                                   |
|       ▼                                                   |
| Looker / Vertex AI / Reports                              |
+-----------------------------------------------------------+

Now explain every box.

⸻

Step 3: Why do we need Cloud VPN?

Many beginners ask:

Why can’t Oracle directly upload to GCS?

Because Oracle is inside a private corporate network.

Google Cloud cannot access private servers over the public internet by default.

We need a secure connection.

Possible options:

* Cloud VPN
* Cloud Interconnect
* Partner Interconnect

Cloud VPN creates an encrypted tunnel.

On-Prem
    │
Encrypted Tunnel
    │
Google Cloud

⸻

Step 4: Why do we need a Service Account?

Students often think:

Can’t Python simply upload the file?

No.

Every API call to Google Cloud must be authenticated.

Instead of using a person’s account, we create a Service Account.

Example:

python-loader@project.iam.gserviceaccount.com

This service account represents the application.

⸻

Step 5: Which IAM Roles are Required?

Suppose the Python script uploads files to Cloud Storage.

Minimum permissions:

Purpose	IAM Role
Upload objects to Cloud Storage	roles/storage.objectCreator
Read uploaded objects	roles/storage.objectViewer
Delete or overwrite objects (if required)	roles/storage.objectAdmin
Use Secret Manager	roles/secretmanager.secretAccessor
Write logs	roles/logging.logWriter
Publish monitoring metrics	roles/monitoring.metricWriter

Follow the principle of least privilege. Do not grant Editor or Owner roles to service accounts in production.

⸻

Step 6: Creating the Storage Bucket

Create a bucket such as:

patient-data-raw

Inside it, organize data by date:

raw/
 ├── oracle/
 │    ├── 2026/
 │    │    ├──07/
 │    │    │   ├──18/
 │    │    │       patients.parquet

Why?

Because searching millions of files becomes much easier.

⸻

Step 7: Why use Parquet?

Many beginners ask:

Why not CSV?

Comparison:

CSV	Parquet
Larger file size	Compressed
No schema	Schema included
Slower queries	Faster analytics
More storage cost	Lower storage cost
Row-based	Columnar

BigQuery is optimized for Parquet.

⸻

Step 8: Python Connects to Oracle

Python uses the Oracle client and executes SQL.

Internally:

Oracle
SELECT *
FROM PATIENTS
↓
Oracle sends rows
↓
Python receives rows
↓
Creates Parquet file

⸻

Step 9: Upload to Cloud Storage

Python authenticates using the service account.

Internally:

Python
↓
Cloud Storage API
↓
IAM checks permissions
↓
Bucket receives object

If the service account lacks the correct role, the upload fails with 403 Permission Denied.

⸻

Step 10: Why Cloud Composer?

Instead of manually running Python every day, use Cloud Composer (Apache Airflow) to orchestrate the workflow.

A DAG can perform tasks such as:

Task 1
Extract data
↓
Task 2
Upload to GCS
↓
Task 3
Validate file
↓
Task 4
Load into BigQuery
↓
Task 5
Send success notification

If Task 2 fails, the DAG stops and can retry based on its retry policy.

⸻

Step 11: Loading Data into BigQuery

Cloud Composer triggers a BigQuery Load Job.

Internally:

Cloud Storage
↓
BigQuery reads Parquet
↓
Validates schema
↓
Writes data into table

No intermediate VM is required.

⸻

Step 12: BigQuery IAM Roles

If Composer loads data into BigQuery, the Composer service account typically needs:

Purpose	IAM Role
Create jobs	roles/bigquery.jobUser
Read datasets	roles/bigquery.dataViewer
Write tables	roles/bigquery.dataEditor

If Composer also creates datasets:

roles/bigquery.admin

Use this only when necessary.

⸻

Step 13: Monitoring

Cloud Monitoring tracks metrics such as:

* DAG failures
* Upload latency
* Number of files processed
* Load job duration
* BigQuery errors

Cloud Logging stores logs from Python, Composer, and BigQuery for troubleshooting.

⸻

Step 14: Failure Handling

Examples:

* Oracle unavailable → Retry extraction
* Upload failed → Retry with exponential backoff
* BigQuery schema mismatch → Move file to a failed/ bucket and alert the team
* Network interruption → Resume after connectivity is restored

This ensures the pipeline is resilient.

⸻

Step 15: Security Best Practices

* Store database passwords in Secret Manager, not in code.
* Use Private IP for GCP resources where possible.
* Grant only the minimum IAM roles required.
* Encrypt data in transit (VPN/Interconnect) and at rest (Cloud Storage and BigQuery).
* Enable Cloud Audit Logs to track who accessed data and when.

⸻

Summary of Common Service Accounts

Service Account	Purpose	Recommended Roles
Python Loader SA	Upload files to GCS	roles/storage.objectCreator, roles/storage.objectViewer, roles/secretmanager.secretAccessor, roles/logging.logWriter
Cloud Composer SA	Orchestrate pipeline	roles/composer.worker, roles/storage.objectViewer, roles/bigquery.jobUser, roles/bigquery.dataEditor, roles/logging.logWriter
Dataflow SA (if used)	Run ETL jobs	roles/dataflow.worker, roles/storage.objectAdmin, roles/bigquery.dataEditor, roles/logging.logWriter
Datastream SA (if used)	CDC replication	roles/datastream.admin (for setup), plus storage and BigQuery permissions as required by the destination
BigQuery Load Job SA	Execute load jobs	roles/bigquery.jobUser, roles/bigquery.dataEditor, roles/storage.objectViewer

 