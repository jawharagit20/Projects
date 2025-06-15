# **RMI Chat Application (Secure Group Chat)**

A secure, real-time group chat application built with Java RMI and SSL/TLS encryption.

## 🚀 Features

- **Secure Communication**: SSL/TLS encrypted RMI connections between client and server
- **Remote Callback**: Real-time message updates using RMI callback mechanisms
- **Group Messaging**: All messages are broadcast to connected clients
- **Online User Tracking**: The server maintains a live list of connected users
- **Java Keystore Security**: Uses `.jks` for authentication and trust between server/client
- **Certificate Support**: X.509 certificate and keystore provided for both ends

## 📋 Prerequisites

- **Java 8** or newer
- **keytool** (included in the JDK)
- **RMI Registry** (starts with `rmiregistry`)

## 🛠️ Installation & Setup

### 1. Clone or Extract the Project
```bash
unzip rmi-chat-group-final.zip
cd rmi-chat-group
```

### 2. Generate SSL Keystores (If Needed)
```bash
sh keystore_script.sh
```

### 3. Compile the Java Classes
```bash
javac *.java
```

### 4. Start the RMI Registry
```bash
rmiregistry
```

Leave this terminal running in the background.

## 🚀 Running the Application

### Start the Server
```bash
java ChatServerRMI
```

### Start the Client
In another terminal:
```bash
java ChatClientRMI
```

1. The client connects securely to the server
2. Messages sent are received in real-time via RMI callback
3. All clients receive messages from each other

## 🏗️ Architecture

### Core Components

| File | Description |
|------|-------------|
| `ChatServerRMI.java` | RMI server managing clients and broadcasting messages |
| `ChatClientRMI.java` | Command-line client with SSL connection and callback handling |
| `ChatService.java` | Remote interface shared by client and server |
| `ClientCallback.java` | Enables server to push messages to clients |
| `server.jks`, `client.jks` | Java keystores used for SSL identity/trust |
| `keystore_script.sh` | Script to generate certificates and keystores |

### Protocol Overview

```
Registration:
Client connects → Registers itself on the server with callback stub

Messaging:
Client sends → Server receives → Server broadcasts via callback

Disconnection:
Client exits → Server removes from active client list
```

## 🔒 Security Features

- **RMI over SSL**: Secure communication using custom `RMISocketFactory`
- **Certificate Validation**: Mutual authentication using keystores and certificates
- **KeyStore Management**: Auto-generated or manual setup using `keytool`

## 📱 Usage Examples

### Basic Flow
1. **Server**: Launches and listens over RMI with secure SSL
2. **Client A**: Connects to server, sends a message
3. **Client B**: Connects and receives messages from A in real-time

### Advanced Features
- **Keystore Trust**: Both client and server validate SSL trust
- **RMI Callback**: No polling — server notifies clients directly
- **Multiple Clients**: Multiple clients can chat simultaneously

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `rmiregistry` not found | Ensure Java is installed and in your PATH |
| SSL handshake failed | Check `server.jks` and `client.jks` match trust setup |
| Port in use | Change the port number in `ChatServerRMI.java` and recompile |
| Class not found | Ensure you are in the correct directory when running `java` |

## 🔧 Configuration

### Default Settings
- **RMI Port**: Default (no need to specify unless customized)
- **Keystore Alias**: `serverkey` / `clientkey`
- **Keystore Password**: `password`
- **SSL Algorithm**: RSA, 2048-bit

### Customize
You can modify server host or keystore path by editing:
```java
System.setProperty("javax.net.ssl.keyStore", "server.jks");
System.setProperty("javax.net.ssl.trustStore", "server.jks");
```

## 📄 File Structure

```
rmi-chat-group/
├── ChatServerRMI.java       # RMI Server
├── ChatClientRMI.java       # RMI Client
├── ChatService.java         # Remote interface
├── ClientCallback.java      # Client-side callback interface
├── client.jks               # Keystore for client
├── server.jks               # Keystore for server
├── server.crt               # SSL certificate
├── keystore_script.sh       # Bash script to generate keystores
└── README.md                # This file
```

## 📝 License

This project is for academic and demonstration purposes.  
Feel free to modify and reuse with credit.

---

**Secure RMI Chatting Made Easy!** 🔐💬