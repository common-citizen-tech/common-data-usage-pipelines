#!/bin/bash

set -euo pipefail

# load dotenv file vars
# https://gist.github.com/mihow/9c7f559807069a03e302605691f85572?permalink_comment_id=4099982#gistcomment-4099982
export "$(grep -vE "^(#.*|\s*)$" .env)"

# Check if the GCP_PROJECT environment variable is set
if [ -z "$GCP_PROJECT" ]; then
    echo "Error: GCP_PROJECT environment variable is not set."
    exit 1
fi

# Check if the GCP_BUCKET environment variable is set
if [ -z "$GCP_BUCKET" ]; then
    echo "Error: GCP_BUCKET environment variable is not set."
    exit 1
fi

# Verify if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud command not found. Please make sure the Google Cloud SDK is installed."
    exit 1
fi

# Check if the specified project exists
if ! gcloud projects describe "$GCP_PROJECT" &> /dev/null; then
    echo "Error: Google Cloud project '$GCP_PROJECT' does not exist."
    exit 1
fi

# Check if the specified bucket exists
if ! gcloud --project="$GCP_PROJECT" storage buckets describe "gs://$GCP_BUCKET"  &> /dev/null; then
    echo "Error: Google Cloud Storage bucket '$GCP_BUCKET' does not exist."
    exit 1
fi

# Perform the rsync operation
gcloud --project "$GCP_PROJECT" storage rsync artifacts "gs://$GCP_BUCKET/artifacts" --recursive

echo "Rsync completed successfully."