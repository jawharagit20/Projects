# 💬 RMI Chat Application (Secure Group Chat)

Une application de chat en groupe développée en Java, utilisant **RMI (Remote Method Invocation)** avec **authentification sécurisée via SSL**.

## 📦 Structure du projet

- `ChatClientRMI.java` : Client du chat RMI.
- `ChatServerRMI.java` : Serveur RMI qui gère les connexions.
- `ChatService.java` : Interface distante partagée entre le client et le serveur.
- `ClientCallback.java` : Permet au serveur d’envoyer des messages au client.
- `client.jks`, `server.jks`, `server.crt` : Certificats SSL pour authentification.
- `keystore_script.sh` : Script de génération des keystores/certificats.

---

## ✅ Fonctionnalités

- Connexion sécurisée entre client et serveur via SSL.
- Système de chat multi-utilisateur.
- Récupération de messages via callback RMI.
- Enregistrement du client dans le keystore.

---

## 🚀 Lancement du projet

### 1. Générer les keystores (optionnel si déjà fournis)

```bash
sh keystore_script.sh
```

### 2. Compiler les fichiers Java

```bash
javac *.java
```

### 3. Démarrer le registre RMI

```bash
rmiregistry
```

Laisser cette commande tourner en arrière-plan.

### 4. Lancer le serveur

```bash
java ChatServerRMI
```

### 5. Lancer le client

Dans une autre console :

```bash
java ChatClientRMI
```

---

## 🔒 Sécurité

Le projet utilise :

- Certificats X.509 auto-signés.
- Java Keystore (`.jks`) pour sécuriser les communications.
- SSL SocketFactory pour créer des connexions sécurisées.

---

## 📚 Prérequis

- JDK 8 ou plus
- Terminal Bash (pour exécuter les scripts)
- `keytool` (inclus dans le JDK)

---

## 📁 Remarques

- Le projet est une version de démonstration d’un système de chat sécurisé.
- Vous pouvez ajouter une interface graphique ou enregistrer les messages dans un fichier pour plus de fonctionnalités.

---

## 👤 Auteur

Projet éducatif — à compléter par les auteurs si nécessaire.