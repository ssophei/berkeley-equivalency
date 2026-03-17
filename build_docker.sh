#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="berkeley-equivalency:latest"

docker build -t "$IMAGE_NAME" -f Dockerfile .

echo "Built image $IMAGE_NAME" 