# Simple Corporate Chat

**Simple Corporate Chat** est une application Java de messagerie en groupe conçue pour un usage en entreprise. Elle repose sur une architecture client-serveur en utilisant à la fois **RPC (Remote Procedure Call)** et **RMI (Remote Method Invocation)** pour faciliter la communication entre clients et serveur.

```

## 🚀 Fonctionnalités

- Système de messagerie instantanée en réseau local
- Connexion multi-utilisateurs avec authentification simple
- Communication client-serveur via **RMI** pour des appels de méthodes distants
- Implémentation de principes **RPC** pour simuler une interface distribuée
- Interface en ligne de commande intuitive

## 🔧 Prérequis

- Java JDK (version 8 ou supérieure)
- Configuration autorisant l'exécution RMI (ports ouverts, permissions réseau)

## 🛠️ Compilation et exécution

### 1. Compilation

```bash
javac ChatServer.java ChatClient.java ChatProtocol.java
```

### 2. Lancement du registre RMI (si requis)

```bash
rmiregistry
```

> Exécutez cette commande dans le dossier contenant les `.class` ou spécifiez le chemin du registre.

### 3. Lancement du serveur

```bash
java ChatServer
```

### 4. Lancement du client

```bash
java ChatClient
```

> ⚠️ Le client doit être lancé après le démarrage du serveur et du registre RMI.

## 👥 Gestion des utilisateurs

Le fichier `users.txt` contient la liste des utilisateurs autorisés à se connecter. Chaque ligne correspond à un nom d'utilisateur unique.

## 🔐 Sécurité

Bien que l'application soit conçue pour un usage pédagogique ou interne, des améliorations peuvent être ajoutées :
- Chiffrement des communications
- Authentification avancée
- Historique des messages

## 📄 Licence

Projet académique ou de démonstration. Libre à des fins d'apprentissage, sans garantie commerciale.
