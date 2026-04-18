#!/bin/bash

PROJECT_ID=data-engineering-488013
REGION=us-central1
BUCKET=datavip-dataflow
SA=sql-bot-sa

echo "Setting project..."
gcloud config set project $PROJECT_ID

echo "Enabling APIs..."
gcloud services enable dataflow.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable compute.googleapis.com

echo "Creating bucket (if not exists)..."
gcloud storage buckets create gs://$BUCKET \
  --project=$PROJECT_ID \
  --location=$REGION || echo "Bucket already exists"

echo "Creating service account..."
gcloud iam service-accounts create $SA \
  --display-name="Dataflow Service Account" || echo "SA exists"

SA_EMAIL=$SA@$PROJECT_ID.iam.gserviceaccount.com

echo "Assigning roles..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/dataflow.worker"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/bigquery.jobUser"

echo "Creating BigQuery dataset..."
bq --location=US mk --dataset $PROJECT_ID:conversational_demo_df || echo "Dataset exists"

echo "Setup completed ✅"
