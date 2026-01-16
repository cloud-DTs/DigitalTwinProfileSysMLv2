#!/bin/bash
set -e
export $(grep -v '^#' .env | xargs)
docker build -t sysml.jupyter -f Dockerfile.jupyter .
docker build -t sysml.api     -f Dockerfile.api     .
docker-compose up -d 
echo "Waiting for API server on localhost:9000..."
until curl -s http://localhost:9000 >/dev/null; do
    echo -n "."
    sleep 2
done