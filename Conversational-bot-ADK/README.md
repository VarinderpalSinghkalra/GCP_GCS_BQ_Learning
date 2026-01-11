# Issue Management Agent (ADK)

## Overview
This project implements an ADK-compatible Issue Management Agent using:
- Vertex AI Agents
- Gemini 2.5
- Firestore
- Pub/Sub
- Cloud Tasks

## Capabilities
- Incident creation
- SLA calculation
- Automated lifecycle
- Status tracking
- Analytics-ready events

## Deployment
1. Deploy Cloud Function:
   gcloud functions deploy update_issue_status \
     --runtime python311 \
     --trigger-http \
     --allow-unauthenticated

2. Create Pub/Sub topic:
   gcloud pubsub topics create issues-topic

3. Create Cloud Tasks queue:
   gcloud tasks queues create issue-status-queue \
     --location us-central1

4. Register agent in Vertex AI Agent Builder

## Usage Examples
- "My VPN is down, high priority"
- "What is the status of INC-AB1234CD?"
