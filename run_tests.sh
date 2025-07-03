#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="berkeley-equivalency:latest"

# Build the image if it doesn't exist
if [ -z "$(docker images -q "$IMAGE_NAME" 2> /dev/null)" ]; then
  ./build_docker.sh
fi

# Run tests inside the built image without mounting any volumes
docker run --rm \
  -e PYTHONASYNCIODEBUG=1 \
  -w /app \
  "$IMAGE_NAME" \
  uv run pytest -q tests "$@"