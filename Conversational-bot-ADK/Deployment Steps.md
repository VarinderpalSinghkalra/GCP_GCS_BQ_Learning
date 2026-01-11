#  Issue Management Agent – Deployment Steps (GCP + ADK)

This document covers **end-to-end deployment** for the Issue Management Agent using:

* Vertex AI (ADK / Agents)
* Firestore
* Pub/Sub
* Cloud Tasks
* Cloud Functions
* Gemini 2.5

---

## 1️⃣ Prerequisites

### 1.1 Install & Login

```bash
gcloud components update
gcloud auth login
gcloud auth application-default login
```

---

### 1.2 Set Project & Region

```bash
gcloud config set project data-engineering-479617
gcloud config set run/region us-central1
```

---

## 2️⃣ Enable Required APIs

```bash
gcloud services enable \
  firestore.googleapis.com \
  pubsub.googleapis.com \
  cloudtasks.googleapis.com \
  cloudfunctions.googleapis.com \
  aiplatform.googleapis.com \
  generativelanguage.googleapis.com
```

---

## 3️⃣ Firestore Setup

### 3.1 Create Firestore (Native Mode)

```bash
gcloud firestore databases create \
  --location=us-central1 \
  --type=firestore-native
```

> ⚠️ Run this **only once** per project.

---

## 4️⃣ Pub/Sub Setup

### 4.1 Create Topic

```bash
gcloud pubsub topics create issues-topic
```

---

### 4.2 (Optional) Create BigQuery Subscription

```bash
gcloud pubsub subscriptions create issues-bq-sub \
  --topic=issues-topic \
  --bigquery-table=data-engineering-479617:analytics.issue_events \
  --use-topic-schema
```

---

## 5️⃣ Cloud Tasks Setup

### 5.1 Create Queue

```bash
gcloud tasks queues create issue-status-queue \
  --location us-central1
```

---

## 6️⃣ Service Account & IAM

### 6.1 Get Default Compute Service Account

```bash
PROJECT_NUMBER=$(gcloud projects describe data-engineering-479617 \
  --format="value(projectNumber)")

SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
```

---

### 6.2 Grant Required Roles

```bash
gcloud projects add-iam-policy-binding data-engineering-479617 \
  --member="serviceAccount:${SA}" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding data-engineering-479617 \
  --member="serviceAccount:${SA}" \
  --role="roles/pubsub.publisher"

gcloud projects add-iam-policy-binding data-engineering-479617 \
  --member="serviceAccount:${SA}" \
  --role="roles/cloudtasks.enqueuer"

gcloud projects add-iam-policy-binding data-engineering-479617 \
  --member="serviceAccount:${SA}" \
  --role="roles/aiplatform.user"
```

---

## 7️⃣ Deploy Cloud Function (Lifecycle Updates)

From project root:

```bash
cd cloud_functions
```

```bash
gcloud functions deploy update_issue_status \
  --runtime python311 \
  --region us-central1 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point update_issue_status
```

---

## 8️⃣ Environment Variables

### 8.1 Set Environment Variables (Optional)

```bash
gcloud functions deploy update_issue_status \
  --set-env-vars \
  GOOGLE_CLOUD_PROJECT=data-engineering-479617,\
  GCP_LOCATION=us-central1,\
  GEMINI_MODEL=gemini-2.5-flash
```

---

##  Vertex AI Agent (ADK)

### 9.1 Upload Tools & Agent Code

```bash
pip install -r requirements.txt
```

---

### 9.2 Create Agent (CLI – Preview)

```bash
gcloud alpha ai agents create \
  --display-name="Issue Management Agent" \
  --region=us-central1
```

---

### 9.3 Attach Tools

In **Vertex AI → Agent Builder UI**:

* Add tools:

  * `submit_issue_tool`
  * `get_issue_status_tool`
* Upload `agent/instructions.md`
* Select model: `gemini-2.5-flash`

---

##  Verification Commands

### 10.1 Test Pub/Sub

```bash
gcloud pubsub topics publish issues-topic \
  --message '{"test":"ok"}'
```

---

### 10.2 Test Cloud Tasks Queue

```bash
gcloud tasks queues describe issue-status-queue \
  --location us-central1
```

---

### 10.3 Firestore Check

```bash
gcloud firestore documents list issues
```

---

## Example Agent Prompts

```
"My VPN is down, priority P1"
"What is the status of INC-AB12CD34?"
```

---

##  Production Notes

* All APIs return **HTTP 200**
* Agent never crashes
* SLA is computed at creation
* Pub/Sub events are analytics-ready
* Cloud Tasks handles lifecycle automatically

---




Just say the word 👌
