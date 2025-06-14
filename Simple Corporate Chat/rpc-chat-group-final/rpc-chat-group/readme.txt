RPC Group-Chat Project (Updated)
================================

Overview
--------
A simple group-chat application over plain TCP sockets using a custom RPC protocol.
Features:
  • User registration & login (passwords hashed with SHA-256, stored in users.txt).
  • Group chat with “bubble” UI in the client.
  • On login, the client receives the full chat history without triggering pop-up notifications.
  • Clients see only truly new messages as pop-ups.
  • A server GUI lets an “admin” broadcast messages (prefixed with “SERVER: …”).
  • Each client sees a live list of other online users (never showing itself).

Files in this folder
--------------------
  • ChatProtocol.java  
      Defines the RPC interface (login, register, broadcast, getHistory).

  • ChatServer.java  
      Listens on port 12345.  
      Maintains credentials in users.txt.  
      Keeps a synchronized chat history list.  
      GUI shows “Online Users” and a “Chat Log.”  
      Broadcasts join/leave and new messages.  
      Ensures history is sent before broadcasting a user’s own “has joined” so no duplicates.

  • ChatClient.java  
      Connects to the server IP:12345.  
      Prompts for server IP, then login/register.  
      Upon login:
        – Registers to receive incoming “MESSAGE …” lines.  
        – Loads all old history with notifications suppressed.  
        – After that, any new message or join/leave from others triggers a pop-up.  
      GUI shows a “bubble” chat area and a list of other online users.

  • users.txt  
      Stores lines of “username:sha256hash.”  
      Initially empty. Each new registration appends a line.

Prerequisites
-------------
  • Java 8 (or newer) installed (javac/java on PATH).  
  • No external libraries required.

How to Compile
--------------
Open a terminal in this folder and run:
    javac ChatProtocol.java ChatServer.java ChatClient.java

This generates:
  • ChatProtocol.class  
  • ChatServer.class  
  • ChatClient.class

How to Run
----------
1) Start the server:
       java ChatServer
   – Server GUI appears:
       • Left pane: “Online Users” (other usernames only).  
       • Center pane: “Chat Log” (all join/leave and messages).  
       • Bottom field: type text and press Enter to broadcast as “SERVER: …”.

2) Start one or more clients (each in its own terminal):
       java ChatClient
   – A dialog asks “Enter server IP:” (type localhost if on the same machine).  
   – Next, a “Login/Register” dialog appears:
       • Enter username/password.  
       • Click “Register” to create a new account (appends to users.txt), or “Login” if already registered.  
   – Once logged in:
       • Client GUI shows:
           – Left pane: list of **other** online users (your own name is hidden).  
           – Right pane: bubble-style chat area.  
       • When the client first opens, it receives all past messages but no pop-up notifications for them.  
       • Only truly new messages or join/leave events from others trigger a pop-up “New Message” dialog.

3) Multiple clients can run simultaneously:
   – Each new client sees the full history (no pop-ups for old messages).  
   – When a client sends a message, it appears as a bubble everywhere and triggers a pop-up on other clients.  
   – When a client joins or leaves, all others see “SERVER: <user> has joined/has left” exactly once (bubble + pop-up).

Notes / Troubleshooting
-----------------------
• **users.txt**  
  – Must exist (even if empty). The server creates it if missing.  
  – Format: `username:hex-encoded-sha256(password)`. Do not edit manually except to remove accounts.

• **Port 12345**  
  – Ensure no firewall or other app is blocking TCP 12345.

• **Pop-up behavior**  
  – Old history never shows pop-ups. Only new messages (and join/leave from others) show pop-ups.

• **Exit behavior**  
  – Closing the client window triggers a “SERVER: <user> has left” broadcast.  
  – Closing the server window stops the server and disconnects all clients.

License
-------
Provided as-is for educational use. Modify or extend freely.
