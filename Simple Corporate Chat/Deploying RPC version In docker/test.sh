#!/bin/bash

# X11 Setup and Testing Script for Chat Application
echo "=== X11 Setup for Docker GUI Applications ==="

# Colors for display
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_cmd() {
    echo -e "${BLUE}[CMD]${NC} $1"
}

# Function to check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check if running in graphical environment
    if [ -z "$DISPLAY" ]; then
        log_error "No graphical display detected (DISPLAY not set)"
        log_info "Make sure you're running this in a desktop environment (GNOME, KDE, XFCE, etc.)"
        return 1
    fi
    
    log_info "Display: $DISPLAY"
    
    # Check if xhost is available
    if ! command -v xhost &> /dev/null; then
        log_warn "xhost not found, installing X11 utilities..."
        sudo apt-get update
        sudo apt-get install -y x11-xserver-utils
    fi
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        return 1
    fi
    
    # Check if X11 socket exists
    if [ ! -d "/tmp/.X11-unix" ]; then
        log_error "X11 socket directory not found: /tmp/.X11-unix"
        return 1
    fi
    
    log_info "All requirements satisfied"
    return 0
}

# Function to setup X11 permissions
setup_x11_permissions() {
    log_info "Setting up X11 permissions for Docker..."
    
    # Allow Docker containers to connect to X server
    log_cmd "xhost +local:docker"
    xhost +local:docker
    
    # Show current X11 socket permissions
    log_info "X11 socket permissions:"
    ls -la /tmp/.X11-unix/
    
    return 0
}

# Function to test X11 forwarding
test_x11_basic() {
    log_info "Testing basic X11 forwarding..."
    
    log_cmd "docker run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix alpine sh -c 'apk add --no-cache openjdk11-jre && java -version'"
    
    if docker run --rm \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
        alpine sh -c 'apk add --no-cache openjdk11-jre && java -version'; then
        log_info "Basic X11 test passed"
        return 0
    else
        log_error "Basic X11 test failed"
        return 1
    fi
}

# Function to test GUI application
test_gui_app() {
    log_info "Testing GUI application (xclock)..."
    
    log_cmd "docker run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix alpine sh -c 'apk add --no-cache xorg-server && xclock'"
    
    log_info "A clock window should appear. Close it to continue."
    log_warn "If no window appears, there might be an X11 forwarding issue."
    
    docker run --rm \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
        alpine sh -c 'apk add --no-cache xorg-server && timeout 10 xclock || true'
    
    return 0
}

# Function to show troubleshooting tips
show_troubleshooting() {
    echo
    log_info "=== Troubleshooting Tips ==="
    echo
    log_info "If GUI applications don't appear:"
    echo "  1. Make sure you're in a graphical desktop environment"
    echo "  2. Check DISPLAY variable: echo \$DISPLAY"
    echo "  3. Restart your display manager:"
    echo "     sudo systemctl restart gdm3    # For GNOME"
    echo "     sudo systemctl restart sddm    # For KDE"
    echo "     sudo systemctl restart lightdm # For XFCE/LXDE"
    echo
    log_info "If permission errors occur:"
    echo "  1. Run: xhost +local:docker"
    echo "  2. Check X11 socket permissions: ls -la /tmp/.X11-unix/"
    echo "  3. Make sure Docker daemon is running: sudo systemctl status docker"
    echo
    log_info "For Wayland users (Ubuntu 22.04+, Fedora):"
    echo "  1. Switch to X11 session (logout and select X11 at login screen)"
    echo "  2. Or set: export DISPLAY=:0"
    echo "  3. Install xwayland: sudo apt-get install xwayland"
    echo
}

# Function to create desktop launcher
create_launcher() {
    log_info "Creating desktop launchers..."
    
    # Server launcher
    cat > ~/Desktop/chat-server.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Chat Server
Comment=Start Chat Server
Exec=bash -c 'cd ~/cour/projects-and-tps/projects/distrubuted_applications_projects && ./deploy.sh start-server'
Icon=network-server
Terminal=true
Categories=Network;
EOF
    
    # Client launcher
    cat > ~/Desktop/chat-client.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Chat Client
Comment=Start Chat Client
Exec=bash -c 'cd ~/cour/projects-and-tps/projects/distrubuted_applications_projects && ./deploy.sh start-client'
Icon=network-workgroup
Terminal=true
Categories=Network;
EOF
    
    chmod +x ~/Desktop/chat-server.desktop
    chmod +x ~/Desktop/chat-client.desktop
    
    log_info "Desktop launchers created:"
    log_info "  - Chat Server: ~/Desktop/chat-server.desktop"
    log_info "  - Chat Client: ~/Desktop/chat-client.desktop"
}

# Main menu
show_menu() {
    echo
    log_info "=== X11 Setup Menu ==="
    echo "1. Check requirements"
    echo "2. Setup X11 permissions"
    echo "3. Test basic X11 forwarding"
    echo "4. Test GUI application"
    echo "5. Create desktop launchers"
    echo "6. Show troubleshooting tips"
    echo "7. Run full setup"
    echo "8. Exit"
    echo
}

# Full setup function
full_setup() {
    log_info "Running full X11 setup..."
    
    if ! check_requirements; then
        log_error "Requirements check failed"
        return 1
    fi
    
    if ! setup_x11_permissions; then
        log_error "X11 permissions setup failed"
        return 1
    fi
    
    if ! test_x11_basic; then
        log_error "Basic X11 test failed"
        show_troubleshooting
        return 1
    fi
    
    log_info "X11 setup completed successfully!"
    log_info "You can now run: ./deploy.sh start-server"
    log_info "And: ./deploy.sh start-client"
    
    return 0
}

# Main script
if [ "$1" == "auto" ]; then
    full_setup
    exit $?
fi

while true; do
    show_menu
    read -p "Choose an option (1-8): " choice
    
    case $choice in
        1) check_requirements ;;
        2) setup_x11_permissions ;;
        3) test_x11_basic ;;
        4) test_gui_app ;;
        5) create_launcher ;;
        6) show_troubleshooting ;;
        7) full_setup ;;
        8) log_info "Exiting..."; exit 0 ;;
        *) log_error "Invalid option" ;;
    esac
    
    echo
    read -p "Press Enter to continue..."
done
