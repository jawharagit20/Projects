# RPC Chat Group

**RPC Chat Group** est une application Java simple de chat en groupe basée sur le modèle client-serveur. Elle utilise le principe d'appel de procédures à distance (RPC) pour permettre à plusieurs clients de se connecter et d'échanger des messages via un serveur central.

## 📦 Structure du projet

```
rpc-chat-group/
├── ChatClient.java         # Code source du client
├── ChatServer.java         # Code source du serveur
├── ChatProtocol.java       # Interface RPC utilisée pour la communication
├── users.txt               # Fichier d'utilisateurs autorisés
├── *.class                 # Fichiers compilés Java
└── readme.txt              # Description textuelle (originale)
```

## 🚀 Fonctionnalités

- Connexion multi-clients à un serveur de chat
- Communication via RPC
- Gestion simple des utilisateurs (via `users.txt`)
- Interface console pour envoyer/recevoir des messages

## 🔧 Prérequis

- Java JDK (version 8 ou supérieure)

## 🛠️ Compilation et exécution

### 1. Compilation

```bash
javac ChatServer.java ChatClient.java ChatProtocol.java
```

### 2. Lancement du serveur

```bash
java ChatServer
```

### 3. Lancement du client

```bash
java ChatClient
```

> ⚠️ Assurez-vous que le serveur est en cours d’exécution avant de démarrer un client.

## 👥 Gestion des utilisateurs

Le fichier `users.txt` contient la liste des utilisateurs autorisés. Chaque ligne représente un utilisateur.

## 📄 Licence

Ce projet est fourni à titre pédagogique. Aucun droit de licence explicite n'est appliqué.
