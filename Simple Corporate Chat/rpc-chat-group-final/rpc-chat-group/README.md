# **RPC Chat Application (Secure Group Chat)**

A secure, real-time group chat application built with Java using SSL/TLS encryption and a custom RPC protocol over TCP sockets.

## 🚀 Features

- **Secure Communication**: SSL/TLS encrypted connections between client and server
- **User Authentication**: Registration and login system with SHA-256 password hashing
- **Real-time Messaging**: Instant message delivery with bubble-style chat interface
- **Chat History**: Complete message history loaded on login without notification spam
- **Online User Tracking**: Live list of connected users (excluding yourself)
- **Smart Notifications**: Pop-up alerts only for new messages, not historical ones
- **Server Administration**: Admin interface for broadcasting server messages
- **Persistent Storage**: User credentials stored securely in encrypted format

## 📋 Prerequisites

- **Java 8** or newer
- **OpenSSL** (for SSL certificate generation)
- No external dependencies required

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd rpc-chat-application
```

### 2. Generate SSL Certificate (First Time Setup)
```bash
keytool -genkeypair -alias chatserver -keyalg RSA -keysize 2048 \
        -keystore server.keystore -storepass chatpass -keypass chatpass \
        -dname "CN=localhost, OU=Chat, O=ChatApp, L=City, S=State, C=US"
```

### 3. Compile the Application
```bash
javac *.java
```

## 🚀 Running the Application

### Start the Server
```bash
java ChatServer
```
The server GUI will appear showing:
- **Online Users Panel**: List of connected clients
- **Chat Log Panel**: All messages and system events
- **Admin Broadcast Field**: Send messages as "SERVER"

### Start Client(s)
```bash
java ChatClient
```

1. Enter server IP address (use `localhost` for local testing)
2. Choose **Login** or **Register**
3. Enter your credentials
4. Start chatting!

## 🏗️ Architecture

### Core Components

| File | Description |
|------|-------------|
| `ChatServer.java` | SSL server handling client connections, authentication, and message broadcasting |
| `ChatClient.java` | GUI client with bubble chat interface and notification system |
| `ChatProtocol.java` | RPC interface defining communication contract |
| `server.keystore` | SSL certificate for secure connections |
| `users.txt` | Encrypted user credentials storage |

### Protocol Overview

```
Authentication Flow:
SUBMITOPTION → LOGIN/REGISTER → SUCCESS/FAIL

Message Flow:
MESSAGE <content> → Broadcast to all clients

System Events:
SERVER: <user> has joined/left
```

## 🎨 User Interface

### Server GUI
- **Real-time monitoring** of all chat activity
- **Online user management** 
- **Admin broadcasting** capabilities
- **Clean, professional interface** with color-coded panels

### Client GUI
- **Modern bubble chat design** with sender identification
- **Timestamp display** for all messages
- **Smart notification system** (only for new messages)
- **Online users sidebar** (excluding self)
- **Responsive layout** with intuitive controls

## 🔒 Security Features

- **SSL/TLS Encryption**: All communication encrypted in transit
- **Password Hashing**: SHA-256 with secure storage
- **Certificate Validation**: Custom trust management for development
- **Session Management**: Secure client-server authentication

## 📱 Usage Examples

### Basic Chat Flow
1. **Server**: Start server → Monitor connections
2. **Client A**: Register → Login → Send message
3. **Client B**: Login → Receive history + new messages
4. **Admin**: Broadcast server announcements

### Advanced Features
- **History Loading**: New users see complete chat history without notification spam
- **Join/Leave Events**: Automatic broadcasting of user status changes
- **Multi-client Support**: Unlimited concurrent connections
- **Graceful Disconnection**: Proper cleanup on client exit

## 🐛 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **SSL Connection Failed** | Regenerate `server.keystore` with correct hostname |
| **Port 12345 in use** | Check for running processes on port 12345 |
| **Login Failed** | Verify credentials or register new account |
| **Users.txt not found** | File is auto-created on first server start |

### Network Configuration
- Ensure **port 12345** is open and available
- For remote connections, use actual server IP instead of `localhost`
- Check firewall settings if connection fails

## 🔧 Configuration

### Default Settings
- **Port**: 12345 (TCP/SSL)
- **Keystore Password**: `chatpass`
- **Hash Algorithm**: SHA-256
- **SSL Protocol**: TLS

### Customization
Modify constants in `ChatServer.java`:
```java
private static final int PORT = 12345;  // Change port
private File usersFile = new File("users.txt");  // Change user storage
```

## 📄 File Structure

```
rpc-chat-application/
├── ChatServer.java      # Main server implementation
├── ChatClient.java      # GUI client application
├── ChatProtocol.java    # RPC interface definition
├── server.keystore      # SSL certificate
├── users.txt           # User credentials (auto-generated)
└── README.md           # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is provided as-is for educational purposes. Feel free to modify and extend for your needs.

## 🙏 Acknowledgments

- Built with Java Swing for cross-platform GUI support
- SSL/TLS implementation using Java's built-in security libraries
- Custom RPC protocol for efficient client-server communication

---

**Happy Chatting!** 💬✨