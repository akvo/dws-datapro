#!/bin/bash
# This script updates the app name in the frontend/public/index.html and app/app.json files.
# Usage: ./update-app-name.sh
if [ ! -f .env ]; then
  echo ".env file not found. Please create a .env file with APP_NAME variable."
  exit 1
fi

# Load environment variables from .env file
if [ -f .env ]; then
  # Use source instead of export with grep/xargs to properly handle spaces
  source .env
fi

# Check if APP_NAME is set
if [ -z "$APP_NAME" ]; then
  echo "APP_NAME is not set in the .env file. Please set it before running this script."
  exit 1
fi

# Put APP_NAME into frontend/public/index.html
sed -i "s|<title>.*</title>|<title>${APP_NAME}</title>|" frontend/public/index.html
# Put APP_NAME into app/app.json in expo > name
sed -i "s|\"name\": \".*\"|\"name\": \"${APP_NAME}\"|" app/app.json
