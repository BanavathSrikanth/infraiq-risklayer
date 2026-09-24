#!/usr/bin/env bash
set -euo pipefail

: "${ACR_LOGIN_SERVER:?Set ACR_LOGIN_SERVER to the existing registry login server}"
: "${IMAGE_REPOSITORY:?Set IMAGE_REPOSITORY}"
: "${IMAGE_TAG:?Set IMAGE_TAG}"
: "${NAMESPACE:?Set NAMESPACE}"

command -v kubectl >/dev/null || { echo "kubectl is required" >&2; exit 127; }
command -v envsubst >/dev/null || { echo "envsubst is required" >&2; exit 127; }

envsubst '${ACR_LOGIN_SERVER} ${IMAGE_REPOSITORY} ${IMAGE_TAG} ${NAMESPACE}' \
  < deploy/kubernetes/ai-orchestration.yaml.template \
  | kubectl apply -f -
