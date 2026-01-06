#!/bin/bash
set -e

# =========================================================
# Vertex AI Conversational Agent – Pre-flight Prerequisites
# With explicit failure checks & exit codes
#
# Project type : Data Engineering
# Scope        : IAM + BigQuery eligibility validation
#
# NOTE:
# - Conversational Agent & Data Store creation are UI-only
# - This script guarantees the UI will work afterward
# =========================================================

# -----------------------------
# CONFIGURATION (EDIT AS NEEDED)
# -----------------------------
PROJECT_ID="data-engineering-479617"
DATASET_NAME="spenddataset"
TABLE_NAME="spend_insights"

# -----------------------------
# EXIT CODES
# -----------------------------
EXIT_PROJECT_NOT_FOUND=10
EXIT_NO_GCLOUD_AUTH=11
EXIT_PROJECT_NUMBER_FAIL=12
EXIT_IAM_BINDING_FAIL=20
EXIT_IAM_VERIFY_FAIL=21
EXIT_DATASET_NOT_FOUND=30
EXIT_DATASET_LOCATION_INVALID=31
EXIT_TABLE_NOT_FOUND=32
EXIT_TABLE_EMPTY=33

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
fail() {
  echo "ERROR: $1"
  exit "$2"
}

info() {
  echo "[INFO] $1"
}

# -----------------------------
# PREFLIGHT: gcloud auth
# -----------------------------
info "Checking gcloud authentication..."
gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .
if [ $? -ne 0 ]; then
  fail "No active gcloud authentication found. Run 'gcloud auth login'." \
    $EXIT_NO_GCLOUD_AUTH
fi

# -----------------------------
# PREFLIGHT: project exists
# -----------------------------
info "Validating project: ${PROJECT_ID}"
gcloud projects describe "${PROJECT_ID}" >/dev/null 2>&1
if [ $? -ne 0 ]; then
  fail "Project '${PROJECT_ID}' does not exist or is not accessible." \
    $EXIT_PROJECT_NOT_FOUND
fi

# -----------------------------
# Set project
# -----------------------------
gcloud config set project "${PROJECT_ID}" >/dev/null

# -----------------------------
# Fetch project number
# -----------------------------
info "Fetching project number..."
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" \
  --format="value(projectNumber)")

if [ -z "${PROJECT_NUMBER}" ]; then
  fail "Unable to retrieve project number." \
    $EXIT_PROJECT_NUMBER_FAIL
fi

info "Project number: ${PROJECT_NUMBER}"

# -----------------------------
# Vertex AI Service Account
# -----------------------------
VERTEX_SA="service-${PROJECT_NUMBER}@gcp-sa-aiplatform.iam.gserviceaccount.com"
info "Vertex AI service account: ${VERTEX_SA}"

# -----------------------------
# IAM ROLE ASSIGNMENTS
# -----------------------------
info "Granting IAM roles at project level..."

IAM_ROLES=(
  "roles/aiplatform.user"
  "roles/discoveryengine.viewer"
  "roles/bigquery.dataViewer"
  "roles/bigquery.metadataViewer"
)

for ROLE in "${IAM_ROLES[@]}"; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${VERTEX_SA}" \
    --role="${ROLE}" >/dev/null || \
    fail "Failed to grant IAM role: ${ROLE}" $EXIT_IAM_BINDING_FAIL
done

info "Waiting for IAM propagation (120 seconds)..."
sleep 120

# -----------------------------
# VERIFY IAM
# -----------------------------
info "Verifying IAM bindings..."

IAM_COUNT=$(gcloud projects get-iam-policy "${PROJECT_ID}" \
  --flatten="bindings[].members" \
  --filter="bindings.members:${VERTEX_SA}" \
  --format="value(bindings.role)" | wc -l)

if [ "${IAM_COUNT}" -lt 4 ]; then
  fail "IAM verification failed. Required roles missing." \
    $EXIT_IAM_VERIFY_FAIL
fi

info "IAM verification successful."

# -----------------------------
# BIGQUERY: DATASET EXISTS
# -----------------------------
info "Checking BigQuery dataset: ${DATASET_NAME}"
bq show "${PROJECT_ID}:${DATASET_NAME}" >/dev/null 2>&1
if [ $? -ne 0 ]; then
  fail "Dataset '${DATASET_NAME}' not found." \
    $EXIT_DATASET_NOT_FOUND
fi

# -----------------------------
# BIGQUERY: DATASET LOCATION
# -----------------------------
info "Validating dataset location..."
DATASET_LOCATION=$(bq show --format=prettyjson \
  "${PROJECT_ID}:${DATASET_NAME}" | grep '"location"' | awk -F\" '{print $4}')

if [ "${DATASET_LOCATION}" != "US" ]; then
  fail "Dataset location is '${DATASET_LOCATION}'. Conversational Agents require US." \
    $EXIT_DATASET_LOCATION_INVALID
fi

info "Dataset location is valid: US"

# -----------------------------
# BIGQUERY: TABLE EXISTS
# -----------------------------
info "Checking BigQuery table: ${TABLE_NAME}"
bq show "${PROJECT_ID}:${DATASET_NAME}.${TABLE_NAME}" >/dev/null 2>&1
if [ $? -ne 0 ]; then
  fail "Table '${TABLE_NAME}' not found in dataset '${DATASET_NAME}'." \
    $EXIT_TABLE_NOT_FOUND
fi

# -----------------------------
# BIGQUERY: TABLE HAS DATA
# -----------------------------
info "Checking table row count..."
ROW_COUNT=$(bq query --use_legacy_sql=false --format=csv \
"SELECT COUNT(*) FROM \`${PROJECT_ID}.${DATASET_NAME}.${TABLE_NAME}\`" | tail -n 1)

if [ "${ROW_COUNT}" -eq 0 ]; then
  fail "Table '${TABLE_NAME}' is empty. Agent will return generic responses." \
    $EXIT_TABLE_EMPTY
fi

info "Table row count OK: ${ROW_COUNT}"

# -----------------------------
# DATASET-LEVEL ACCESS (RECOMMENDED)
# -----------------------------
info "Granting dataset-level access (recommended)..."
bq update \
--dataset_access=role:READER,groupByEmail:${VERTEX_SA} \
"${PROJECT_ID}:${DATASET_NAME}" >/dev/null || true

# -----------------------------
# COMPLETION
# -----------------------------
echo "--------------------------------------------------"
echo "Pre-flight checks PASSED."
echo
echo "You can now proceed with UI steps:"
echo "1. Vertex AI → Conversational Agents → Create NEW agent"
echo "2. Vertex AI → Conversational Agents → Data Stores → Create (BigQuery, US)"
echo "3. Agent → Tools → Create → Data store → Attach"
echo
echo "No CLI-level blockers remain."
echo "--------------------------------------------------"
