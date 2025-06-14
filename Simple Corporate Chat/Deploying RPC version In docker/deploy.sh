#!/bin/bash

# Deployment script for Chat Application with X11 forwarding

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_cmd()   { echo -e "${BLUE}[CMD]${NC} $1"; }

check_x11() {
    [ -z "$DISPLAY" ] && { log_error "DISPLAY not set"; return 1; }
    command -v xhost >/dev/null 2>&1 || { log_error "Install x11-xserver-utils"; return 1; }
    return 0
}

setup_x11() {
    log_info "Setting up X11 permissions..."
    xhost +local:docker >/dev/null 2>&1
    xhost +SI:localuser:root >/dev/null 2>&1
    log_info "DISPLAY=$DISPLAY"
    return 0
}

get_host_ip() {
    # get the primary non-loopback IPv4 address
    ip route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if ($i=="src") print $(i+1)}'
}

start_server() {
    log_info "Starting chat server..."
    check_x11 && setup_x11 || return 1

    # remove any existing container
    if docker ps -aq --filter "name=^chat-server\$" | grep -q .; then
        log_info "Removing existing chat-server container"
        docker rm -f chat-server >/dev/null 2>&1
    fi

    docker volume create chat-data >/dev/null 2>&1 || true

    HOST_IP=$(get_host_ip)
    log_info "Server will listen on ${HOST_IP}:12345"

    log_cmd "docker run -d --name chat-server \
      --net=host \
      --user $(id -u):$(id -g) \
      -e DISPLAY=$DISPLAY \
      -v chat-data:/app/data \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      chat-server:latest"
    if docker run -d \
        --name chat-server \
        --net=host \
        --user "$(id -u):$(id -g)" \
        -e DISPLAY="$DISPLAY" \
        -v chat-data:/app/data \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
        chat-server:latest; then
        log_info "Server started at ${HOST_IP}:12345"
    else
        log_error "Failed to start server"
        return 1
    fi
}

start_client() {
    CLIENT="chat-client-$(date +%s)"
    log_info "Starting chat client ($CLIENT)..."
    check_x11 && setup_x11 || return 1

    log_cmd "docker run -d --name $CLIENT \
      --net=host \
      --user $(id -u):$(id -g) \
      -e DISPLAY=$DISPLAY \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      chat-client:latest"
    if docker run -d \
        --name "$CLIENT" \
        --net=host \
        --user "$(id -u):$(id -g)" \
        -e DISPLAY="$DISPLAY" \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
        chat-client:latest; then
        log_info "Client started ($CLIENT)"
    else
        log_error "Failed to start client"
        return 1
    fi
}

stop_containers() {
    log_info "Stopping chat-server"
    docker rm -f chat-server >/dev/null 2>&1 || true
    for c in $(docker ps -q --filter "name=chat-client-"); do
        docker rm -f "$c" >/dev/null 2>&1
    done
    xhost -local:docker >/dev/null 2>&1
    xhost -SI:localuser:root >/dev/null 2>&1
    log_info "Stopped all"
}

show_status() {
    docker ps --filter "name=chat-server" --filter "name=chat-client-" \
        --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo "DISPLAY=$DISPLAY"
}

show_logs() {
    case "$1" in
      server) docker logs -f chat-server ;;
      client)
        read -p "Client name: " C
        docker logs -f "$C"
        ;;
      *) log_error "Use 'logs-server' or 'logs-client'" ;;
    esac
}

case "$1" in
  start-server) start_server ;;
  start-client) start_client ;;
  stop)         stop_containers ;;
  status)       show_status ;;
  logs-server)  show_logs server ;;
  logs-client)  show_logs client ;;
  help|*) 
    echo "Usage: $0 {start-server|start-client|stop|status|logs-server|logs-client}"
    ;;
esac

