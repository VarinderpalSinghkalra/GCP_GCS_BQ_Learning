# Google Cloud CLI Reference (Condensed)

> A single-file reference of commonly used Google Cloud CLI commands.
> Covers the core commands used by Cloud Engineers, Data Engineers, and Cloud Architects.

---

# Authentication & Configuration

```bash
gcloud version
gcloud info
gcloud init
gcloud auth login
gcloud auth application-default login
gcloud auth list
gcloud config list
gcloud config set project PROJECT_ID
gcloud config get-value project
gcloud config configurations list
gcloud config configurations create dev
gcloud config configurations activate dev
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
```

# Projects

```bash
gcloud projects list
gcloud projects create PROJECT_ID
gcloud projects describe PROJECT_ID
gcloud projects delete PROJECT_ID
```

# APIs

```bash
gcloud services list
gcloud services list --enabled
gcloud services enable compute.googleapis.com
gcloud services disable compute.googleapis.com
```

# IAM

```bash
gcloud iam service-accounts list
gcloud iam service-accounts create my-sa
gcloud iam service-accounts delete my-sa@PROJECT_ID.iam.gserviceaccount.com
gcloud iam service-accounts keys create key.json \
  --iam-account=my-sa@PROJECT_ID.iam.gserviceaccount.com
gcloud iam service-accounts keys list \
  --iam-account=my-sa@PROJECT_ID.iam.gserviceaccount.com
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:my-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/editor"
gcloud iam roles list
```

# Compute Engine

```bash
gcloud compute instances list
gcloud compute instances create vm1
gcloud compute instances start vm1
gcloud compute instances stop vm1
gcloud compute instances reset vm1
gcloud compute instances delete vm1
gcloud compute ssh vm1
gcloud compute scp file.txt vm1:~
gcloud compute disks list
gcloud compute images list
gcloud compute snapshots list
```

# VPC

```bash
gcloud compute networks list
gcloud compute networks create my-vpc --subnet-mode=custom
gcloud compute subnetworks list
gcloud compute firewall-rules list
gcloud compute firewall-rules create allow-http \
  --allow=tcp:80
gcloud compute routes list
gcloud compute addresses list
```

# Cloud Storage

```bash
gcloud storage buckets list
gcloud storage buckets create gs://bucket-name
gcloud storage ls
gcloud storage cp file.csv gs://bucket-name/
gcloud storage cp gs://bucket-name/file.csv .
gcloud storage rsync ./data gs://bucket-name
gcloud storage rm gs://bucket-name/file.csv
gcloud storage buckets describe gs://bucket-name
```

# BigQuery

```bash
bq ls
bq mk dataset
bq show dataset
bq query
bq load
bq extract
bq cp
bq rm dataset
bq ls -j
```

# Pub/Sub

```bash
gcloud pubsub topics list
gcloud pubsub topics create topic1
gcloud pubsub topics publish topic1 --message="Hello"
gcloud pubsub subscriptions create sub1 --topic=topic1
gcloud pubsub subscriptions pull sub1
gcloud pubsub subscriptions delete sub1
```

# Dataflow

```bash
gcloud dataflow jobs list
gcloud dataflow jobs describe JOB_ID
gcloud dataflow jobs cancel JOB_ID
gcloud dataflow templates run
gcloud dataflow flex-template run
```

# Dataproc

```bash
gcloud dataproc clusters list
gcloud dataproc clusters create cluster1
gcloud dataproc jobs submit pyspark script.py
gcloud dataproc clusters delete cluster1
```

# Composer

```bash
gcloud composer environments list
gcloud composer environments create composer1
gcloud composer environments run composer1 dags list
```

# GKE

```bash
gcloud container clusters list
gcloud container clusters create cluster1
gcloud container clusters get-credentials cluster1
kubectl get pods
kubectl get deployments
kubectl get svc
kubectl logs POD
```

# Cloud Run

```bash
gcloud run services list
gcloud run deploy
gcloud run services describe SERVICE
gcloud run jobs execute JOB
```

# Cloud Functions

```bash
gcloud functions list
gcloud functions deploy
gcloud functions call FUNCTION
gcloud functions delete FUNCTION
```

# Cloud SQL

```bash
gcloud sql instances list
gcloud sql instances create
gcloud sql databases create
gcloud sql users create
gcloud sql backups list
```

# Artifact Registry

```bash
gcloud artifacts repositories list
gcloud artifacts repositories create
gcloud artifacts docker images list
```

# Secret Manager

```bash
gcloud secrets list
gcloud secrets create my-secret
gcloud secrets versions add my-secret
gcloud secrets versions access latest --secret=my-secret
```

# Cloud Build

```bash
gcloud builds submit
gcloud builds list
gcloud builds log BUILD_ID
gcloud builds triggers list
```

# Logging

```bash
gcloud logging logs list
gcloud logging read
gcloud logging sinks list
```

# Monitoring

```bash
gcloud monitoring dashboards list
gcloud monitoring policies list
```

# Scheduler

```bash
gcloud scheduler jobs list
gcloud scheduler jobs create http
gcloud scheduler jobs create pubsub
```

# DNS

```bash
gcloud dns managed-zones list
gcloud dns record-sets list
```

# KMS

```bash
gcloud kms keyrings list
gcloud kms keys list
gcloud kms encrypt
gcloud kms decrypt
```

# Vertex AI

```bash
gcloud ai models list
gcloud ai endpoints list
gcloud ai custom-jobs create
```

# Billing

```bash
gcloud billing accounts list
gcloud billing projects link
```

# Useful Help

```bash
gcloud help
gcloud topic configurations
gcloud topic filters
gcloud topic formats
```
