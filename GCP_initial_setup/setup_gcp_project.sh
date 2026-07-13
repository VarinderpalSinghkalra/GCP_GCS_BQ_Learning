#!/usr/bin/env bash
set -euo pipefail

# ============================================
# Validate input
# ============================================

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 config.env"
    exit 1
fi

if [[ ! -f "$1" ]]; then
    echo "Error: Config file '$1' not found."
    exit 1
fi

# Load configuration
source "$1"

echo "======================================"
echo "Google Cloud Project Setup"
echo "======================================"
echo "Project ID : $PROJECT_ID"
echo "Region     : $DEFAULT_REGION"
echo "Zone       : $DEFAULT_ZONE"
echo

# Validate required variables
if [[ -z "${PROJECT_ID:-}" ]]; then
    echo "PROJECT_ID is missing in config.env"
    exit 1
fi

if [[ -z "${BILLING_ACCOUNT:-}" ]]; then
    echo "BILLING_ACCOUNT is missing in config.env"
    exit 1
fi

# ============================================
# Create Project
# ============================================

if gcloud projects describe "$PROJECT_ID" >/dev/null 2>&1; then
    echo "Project already exists."
else
    echo "Creating project..."

    if [[ -n "${ORG_ID:-}" ]]; then
        gcloud projects create "$PROJECT_ID" \
            --organization="$ORG_ID"

    elif [[ -n "${FOLDER_ID:-}" ]]; then
        gcloud projects create "$PROJECT_ID" \
            --folder="$FOLDER_ID"

    else
        gcloud projects create "$PROJECT_ID"
    fi
fi

# ============================================
# Link Billing
# ============================================

echo "Linking billing account..."

gcloud beta billing projects link "$PROJECT_ID" \
    --billing-account="$BILLING_ACCOUNT"

# ============================================
# Set Default Configuration
# ============================================

gcloud config set project "$PROJECT_ID"
gcloud config set compute/region "$DEFAULT_REGION"
gcloud config set compute/zone "$DEFAULT_ZONE"

# ============================================
# Enable APIs
# ============================================

echo "Enabling APIs..."

for api in "${APIS[@]}"; do
    echo "Enabling $api"
    gcloud services enable "$api"
done

# ============================================
# Create Network (Optional)
# ============================================

if [[ "${CREATE_NETWORK:-false}" == "true" ]]; then

    if ! gcloud compute networks describe "$VPC_NAME" >/dev/null 2>&1; then

        echo "Creating VPC..."

        gcloud compute networks create "$VPC_NAME" \
            --subnet-mode=custom

        gcloud compute networks subnets create "$SUBNET_NAME" \
            --network="$VPC_NAME" \
            --region="$DEFAULT_REGION" \
            --range="$SUBNET_CIDR"

    else
        echo "VPC already exists."
    fi
fi

echo
echo "======================================"
echo "Project setup completed successfully!"
echo "======================================"