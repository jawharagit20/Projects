#!/bin/bash

# Automated build script for Chat Application
echo "=== Build Script for Chat Application ==="

# Colors for display
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to display messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed or not available in PATH"
    exit 1
fi

# Compile Java files
log_info "Compiling Java files..."
if javac ChatProtocol.java ChatServer.java ChatClient.java; then
    log_info "Compilation successful"
else
    log_error "Error during compilation"
    exit 1
fi

# Build server Docker image
log_info "Building Docker image for server..."
if docker build -f Dockerfile.server -t chat-server:latest .; then
    log_info "Server image created successfully"
else
    log_error "Error creating server image"
    exit 1
fi

# Build client Docker image
log_info "Building Docker image for client..."
if docker build -f Dockerfile.client -t chat-client:latest .; then
    log_info "Client image created successfully"
else
    log_error "Error creating client image"
    exit 1
fi

# Create Docker network
log_info "Creating Docker network..."
docker network create chat-network 2>/dev/null || log_warn "Network already exists"

# Display created images
log_info "Created Docker images:"
docker images | grep -E "(chat-server|chat-client)"

echo
log_info "Build completed successfully!"
log_info "Use './deploy.sh' to deploy the application"
