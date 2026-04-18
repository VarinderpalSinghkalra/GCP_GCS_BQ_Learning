#!/bin/bash

echo "Destroying VMSS..."
cd vmss
terraform destroy -auto-approve

echo "Destroying Storage..."
cd ../storage
terraform destroy -auto-approve

echo "🧹 Cleanup Done"
