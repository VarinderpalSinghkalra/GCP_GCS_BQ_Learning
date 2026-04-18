#!/bin/bash

echo "Logging into Azure..."
az login

echo "Deploying VMSS..."
cd vmss
terraform init
terraform apply -auto-approve

echo "Deploying Storage..."
cd ../storage
terraform init
terraform apply -auto-approve

echo "✅ Deployment Completed"
