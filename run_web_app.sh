#!/bin/bash
cd "$(dirname "$0")" || exit

if [[ ! -f ".env" ]]; then
  echo "Error: You must create and populate a .env file before running this script. See README.md for instructions."
  exit 1
fi

echo "Building docker image..."
docker build -f ./web_app.Dockerfile -t cohelm_web_app .

echo "Running docker image..."
docker run -p 8000:80 -v $(pwd)/database:/app/database -v $(pwd)/.env:/app/.env cohelm_web_app
