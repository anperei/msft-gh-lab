#!/usr/bin/env bash
set -euo pipefail

echo "[preprovision] Checking authentication..."

# Check if logged in to azd (which is what azd up uses)
if azd auth login --check-status > /dev/null 2>&1; then
  echo "[preprovision] Authenticated with azd"
elif az account show > /dev/null 2>&1; then
  echo "[preprovision] Authenticated with Azure CLI"
  SUBSCRIPTION=$(az account show --query name -o tsv)
  echo "[preprovision] Using subscription: $SUBSCRIPTION"
else
  echo "[preprovision] Not logged in. Please run 'azd auth login' or 'az login' first."
  exit 1
fi

echo "[preprovision] Pre-provision checks completed successfully."
