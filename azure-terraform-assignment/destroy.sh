#!/bin/bash

cd vmss
terraform destroy -auto-approve

cd ../storage
terraform destroy -auto-approve
