#!/bin/bash

PROJECT_ID=data-engineering-488013
BUCKET=datavip-dataflow
SA_EMAIL=sql-bot-sa@$PROJECT_ID.iam.gserviceaccount.com

echo "Installing dependencies..."
pip install --user -r requirements.txt

echo "Uploading CSV..."
gcloud storage cp spend_cube_clean.csv gs://$BUCKET/

echo "Running Dataflow job..."

python main.py \
  --runner DataflowRunner \
  --project $PROJECT_ID \
  --region us-central1 \
  --temp_location gs://$BUCKET/temp \
  --staging_location gs://$BUCKET/staging \
  --service_account_email $SA_EMAIL \
  --requirements_file requirements.txt
