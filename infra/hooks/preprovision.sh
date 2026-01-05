#!/usr/bin/env bash
set -euo pipefail

echo "[preprovision] Checking Azure CLI authentication..."

if ! az account show > /dev/null 2>&1; then
  echo "[preprovision] Not logged in to Azure CLI. Please run 'az login' first."
  exit 1
fi

SUBSCRIPTION=$(az account show --query name -o tsv)
echo "[preprovision] Using subscription: $SUBSCRIPTION"
echo "[preprovision] Pre-provision checks completed successfully."
