#!/bin/bash

ENDPOINTS=(
  "http://localhost:5000/health"
  "http://localhost:5001/ready"
  "http://localhost:5002/health"
)

for endpoint in "${ENDPOINTS[@]}"; do
  if curl -s --head --fail "$endpoint" > /dev/null; then
    echo "✅ $endpoint"
  else
    echo "❌ $endpoint"
    exit 1
  fi
done
