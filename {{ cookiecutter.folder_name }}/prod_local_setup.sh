#!/bin/bash
set -euo pipefail

MINIKUBE_PROFILE="airflow"
DOCKER_IMAGE_NAME="my-local-image/kpo-test:v1"

BLUE='\033[0;34m'
NC='\033[0m'

CLEAN_INSTALL=false
if [[ "${1:-}" == "--clean" ]]; then
    CLEAN_INSTALL=true
fi

cleanup() {
    log "Performing cleanup..."

    if command -v minikube >/dev/null 2>&1; then
        if minikube profile list 2>/dev/null | grep -q "^$MINIKUBE_PROFILE "; then
            log "Stopping and deleting profile: $MINIKUBE_PROFILE"
            minikube stop --profile "$MINIKUBE_PROFILE" 2>/dev/null || true
            minikube delete --profile "$MINIKUBE_PROFILE" 2>/dev/null || true
        fi

        if $CLEAN_INSTALL; then
            log "Full cleanup: removing all minikube data"
            minikube delete --all --purge 2>/dev/null || true
            rm -rf ~/.minikube ~/.kube
            sudo rm -f "$(command -v minikube)" 2>/dev/null || true
            install_minikube
        fi
    else
        if $CLEAN_INSTALL; then
            install_minikube
        else
            error "Minikube not found. Please install minikube first or use --clean flag"
            exit 1
        fi
    fi
}

install_minikube() {
    log "Installing minikube..."
    OS=$(uname | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)

    case "$ARCH" in
        x86_64) ARCH="amd64" ;;
        arm64|aarch64) ARCH="arm64" ;;
        *)
            error "Unsupported architecture: $ARCH"
            exit 1
            ;;
    esac

    curl -LO "https://github.com/kubernetes/minikube/releases/latest/download/minikube-${OS}-${ARCH}"
    sudo install "minikube-${OS}-${ARCH}" /usr/local/bin/minikube
    rm "minikube-${OS}-${ARCH}"
    log "Minikube installed"
}

start_minikube() {
  log "Checking Minikube cluster [$MINIKUBE_PROFILE] status..."

  if minikube status --profile "$MINIKUBE_PROFILE" | grep -q "Running"; then
    log "Minikube cluster [$MINIKUBE_PROFILE] is already running. Skipping start."
  else
    log "Starting Minikube cluster [$MINIKUBE_PROFILE]..."
    minikube start --profile "$MINIKUBE_PROFILE" --driver=docker --cpus=4 --memory=4g
  fi

  log "Switching Docker context to Minikube..."
  eval "$(minikube -p "$MINIKUBE_PROFILE" docker-env)"
}


build_docker_image(){
    if [[ ! -f "./Dockerfile" ]]; then
    error_exit "Dockerfile not found"
  fi

  log "Building Docker image [$DOCKER_IMAGE_NAME]..."
  docker build -t  "$DOCKER_IMAGE_NAME"  .
  }

create_secrets() {
  log "Checking if secret [my-minio-creds] exists in Minikube cluster [$MINIKUBE_PROFILE]..."

  if minikube kubectl -p "$MINIKUBE_PROFILE" -- get secret my-minio-creds >/dev/null 2>&1; then
    log "Secret [my-minio-creds] already exists. Skipping creation."
  else
    log "Creating secret [my-minio-creds] in Minikube cluster [$MINIKUBE_PROFILE]..."
    minikube kubectl -p "$MINIKUBE_PROFILE" -- create secret generic my-minio-creds \
      --from-literal=AWS_ACCESS_KEY_ID=minio \
      --from-literal=AWS_SECRET_ACCESS_KEY=minio123
  fi
}


log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

main() {
    log "Starting Prod Local test setup..."

    cleanup
    start_minikube
    build_docker_image
    create_secrets
}

main