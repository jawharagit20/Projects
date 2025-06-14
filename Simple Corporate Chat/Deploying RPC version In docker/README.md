# Distributed Chat Application

A multi-user chat application built with Java Swing and Socket programming, featuring a GUI-based server and client with Docker containerization and X11 forwarding support.

## 🚀 Features

### Server Features
- **Multi-user Support**: Handles multiple concurrent client connections
- **User Authentication**: Secure login and registration system with SHA-256 password hashing
- **Chat History**: Persistent message history for new users joining
- **Real-time Broadcasting**: Instant message delivery to all connected clients
- **Admin Controls**: Server-side message broadcasting capability
- **GUI Interface**: Modern dark-themed server interface with online user list and chat log
- **Persistent Storage**: User credentials stored in encrypted format

### Client Features
- **Modern GUI**: Dark-themed chat interface with message bubbles
- **Real-time Messaging**: Instant message sending and receiving
- **User Presence**: Live online user list
- **Message Notifications**: Pop-up notifications for new messages (with smart suppression during history loading)
- **Responsive Design**: Smooth scrolling and auto-scroll to latest messages
- **Connection Management**: Automatic server connection with IP configuration

### Technical Features
- **Docker Support**: Fully containerized application with separate server and client images
- **X11 Forwarding**: GUI applications running in Docker containers
- **Network Isolation**: Dedicated Docker network for secure communication
- **Automated Deployment**: Complete build and deployment scripts
- **Health Checks**: Container health monitoring
- **Scalability**: Support for multiple client instances

## 📋 Requirements

### System Requirements
- **Operating System**: Linux (Ubuntu 18.04+, Fedora 30+, or similar)
- **Java**: OpenJDK 11 or higher
- **Docker**: Version 20.10 or higher
- **Display Server**: X11 (for GUI applications)
- **Memory**: At least 512MB RAM
- **Storage**: 100MB free space

### Software Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install openjdk-11-jdk docker.io x11-xserver-utils

# Fedora/RHEL
sudo dnf install java-11-openjdk-devel docker xorg-x11-server-utils

# Arch Linux
sudo pacman -S jdk11-openjdk docker xorg-xhost
```

## 🛠️ Installation

### 1. Clone the Repository
```bash
# 1. Clone with no working files
git clone --no-checkout https://github.com/Yassine-El-Ghazi/projects-and-tps.git
cd projects-and-tps

# 2. Turn on sparse-checkout in cone mode
git sparse-checkout init --cone

# 3. Specify the one subdirectory you want
git sparse-checkout set projects/distrubuted_applications_projects

# 4. Check out your branch (e.g. main)
git checkout main
```

### 2. Set Up X11 Forwarding
```bash
# Run the X11 setup script
chmod +x test.sh
./test.sh auto

# Or run interactive setup
./test.sh
```

### 3. Build the Application
```bash
# Make scripts executable
chmod +x build.sh deploy.sh

# Build Docker images
./build.sh
```

## 🚀 Quick Start

### Method 1: Using Deployment Script (Recommended)

#### Start the Server
```bash
./deploy.sh start-server
```

#### Start Client(s)
```bash
./deploy.sh start-client
```

### Method 2: Using Docker Compose
```bash
# Start server
docker-compose up chat-server

# Start client (in another terminal)
docker-compose --profile client up chat-client
```

### Method 3: Manual Docker Commands
```bash
# Create network
docker network create chat-network

# Start server
docker run -d --name chat-server \
    --network chat-network \
    -p 12345:12345 \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    chat-server:latest

# Start client
docker run -d --name chat-client \
    --network chat-network \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    chat-client:latest
```

## 📖 Usage Guide

### First Time Setup

1. **Start the Server**: Run `./deploy.sh start-server`
   - Server GUI will appear showing online users and chat log
   - Server listens on port 12345

2. **Start a Client**: Run `./deploy.sh start-client`
   - Client GUI will appear
   - Enter server IP (use `chat-server` for Docker network, or `localhost` for local)

3. **Create Account**: 
   - Choose "Register" to create a new account
   - Enter username and password
   - Login with your credentials

4. **Start Chatting**:
   - Type messages in the input field
   - Press Enter or click Send
   - View online users in the left panel
   - Messages appear as bubbles in the chat area

### Server Administration

The server provides admin controls:
- **Broadcast Messages**: Type in the server's input field to send messages as "SERVER"
- **Monitor Users**: View all online users in the left panel
- **View Chat Log**: All messages appear in the server's chat log
- **User Management**: Monitor user registrations and logins

### Client Features

- **Message Bubbles**: Your messages appear on the right (green), others on the left (blue)
- **Timestamps**: Each message shows the time it was sent
- **Notifications**: Pop-up notifications for new messages (except during history loading)
- **Auto-scroll**: Chat automatically scrolls to show latest messages
- **Online Users**: Left panel shows all currently connected users

## 🔧 Configuration

### Server Configuration
- **Port**: Default 12345 (configurable in `ChatServer.java`)
- **User File**: `users.txt` (stores encrypted user credentials)
- **Memory**: 256MB max, 128MB initial (configurable in Docker)

### Client Configuration
- **Server Address**: Prompted on startup
- **Display**: Inherits from host system
- **Memory**: Default JVM settings

### Docker Configuration
- **Network**: `chat-network` (bridge mode)
- **Volumes**: `chat-data` for persistent storage
- **Restart Policy**: `unless-stopped`

## 🐳 Docker Commands Reference

### Container Management
```bash
# View status
./deploy.sh status

# Stop all containers
./deploy.sh stop

# View server logs
./deploy.sh logs-server

# View client logs
./deploy.sh logs-client

# Cleanup everything
./deploy.sh cleanup
```

### Manual Docker Operations
```bash
# List running containers
docker ps --filter "name=chat-*"

# View logs
docker logs -f chat-server
docker logs -f chat-client-123456

# Execute commands in container
docker exec -it chat-server bash

# Remove containers
docker rm -f chat-server chat-client-123456
```

## 🔍 Troubleshooting

### Common Issues

#### GUI Not Appearing
```bash
# Check DISPLAY variable
echo $DISPLAY

# Setup X11 permissions
xhost +local:docker

# Test X11 forwarding
./test.sh
```

#### Connection Issues
```bash
# Check if server is running
docker ps --filter "name=chat-server"

# Check server logs
docker logs chat-server

# Test network connectivity
docker exec chat-client ping chat-server
```

#### Permission Errors
```bash
# Fix X11 permissions
xhost +local:docker

# Check Docker permissions
sudo usermod -aG docker $USER
# Logout and login again
```

### Wayland Users (Ubuntu 22.04+)
```bash
# Switch to X11 session at login screen
# Or set environment variable
export DISPLAY=:0

# Install Xwayland
sudo apt-get install xwayland
```

### Network Issues
```bash
# Recreate Docker network
docker network rm chat-network
docker network create chat-network

# Check firewall
sudo ufw allow 12345
```

## 📁 File Structure

```
distributed-chat-application/
├── src/
│   ├── ChatServer.java          # Server application
│   ├── ChatClient.java          # Client application
│   └── ChatProtocol.java        # Communication interface
├── docker/
│   ├── Dockerfile.server        # Server container definition
│   ├── Dockerfile.client        # Client container definition
│   └── docker-compose.yml       # Multi-container setup
├── scripts/
│   ├── build.sh                 # Build automation
│   ├── deploy.sh                # Deployment automation
│   └── test.sh                  # X11 setup and testing
├── data/
│   └── users.txt                # User credentials (auto-generated)
└── README.md                    # This file
```

## 🔒 Security Features

### Password Security
- **SHA-256 Hashing**: All passwords are hashed before storage
- **No Plain Text**: Passwords never stored in plain text
- **Secure Transmission**: Credentials sent over established socket connections

### Container Security
- **Non-root User**: Applications run as non-privileged user
- **Network Isolation**: Containers communicate through dedicated network
- **Resource Limits**: Memory and CPU limits prevent resource exhaustion

### Network Security
- **Port Binding**: Only necessary ports exposed
- **Local Network**: Docker network isolates application traffic
- **Connection Validation**: All client connections validated

## 🧪 Testing

### Unit Testing
```bash
# Compile and run basic tests
javac *.java
java ChatServer &
java ChatClient
```

### Integration Testing
```bash
# Test X11 forwarding
./test.sh

# Test Docker build
./build.sh

# Test deployment
./deploy.sh start-server
./deploy.sh start-client
```

### Load Testing
```bash
# Start multiple clients
for i in {1..5}; do
    ./deploy.sh start-client &
done
```

## 🚀 Deployment Options

### Development Environment
```bash
# Quick development setup
javac *.java
java ChatServer &
java ChatClient
```

### Production Environment
```bash
# Build and deploy with Docker
./build.sh
./deploy.sh start-server
./deploy.sh start-client
```

### Cloud Deployment
```bash
# Build images
docker build -f Dockerfile.server -t your-registry/chat-server .
docker build -f Dockerfile.client -t your-registry/chat-client .

# Push to registry
docker push your-registry/chat-server
docker push your-registry/chat-client
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- Follow Java naming conventions
- Use meaningful variable names
- Add comments for complex logic
- Maintain consistent indentation

### Testing Guidelines
- Test GUI functionality manually
- Verify Docker builds work
- Test on multiple Linux distributions
- Check X11 forwarding on different desktop environments

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Getting Help
- Check the troubleshooting section above
- Review Docker and X11 setup guides
- Open an issue for bugs or feature requests

### Reporting Issues
When reporting issues, please include:
- Operating system and version
- Docker version
- Desktop environment (GNOME, KDE, etc.)
- Error messages and logs
- Steps to reproduce

### Feature Requests
We welcome feature requests! Please describe:
- The desired functionality
- Use case scenarios
- Implementation suggestions

## 📚 Additional Resources

### Documentation
- [Docker Documentation](https://docs.docker.com/)
- [Java Swing Tutorial](https://docs.oracle.com/javase/tutorial/uiswing/)
- [X11 Forwarding Guide](https://wiki.archlinux.org/title/X11_forwarding)

### Related Projects
- Socket Programming in Java
- GUI Development with Swing
- Docker Container Orchestration
- Network Programming Patterns

---

**Distributed Chat Application** - A modern, containerized chat solution with GUI support.
