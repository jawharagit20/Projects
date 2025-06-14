RMI Group-Chat Project (Updated)
================================

Overview
--------
A simple group-chat application built on Java RMI.  
Features:
  • User registration & login (passwords hashed with SHA-256, stored in users.txt).  
  • On login, the client registers its callback immediately so the server’s “Online Users” list updates right away.  
  • The client then fetches all past chat history—with pop-up notifications suppressed—so old messages do not pop up.  
  • After history loads, any new join/leave or chat message from others triggers a pop-up.  
  • Server GUI lets an “admin” broadcast “SERVER: …” messages to all connected clients.  
  • Logout is called when the client window closes so the server’s online list stays in sync.

Files in this folder
--------------------
  • ChatService.java  
      RMI interface defining remote methods:
        – boolean login(String, String)  
        – boolean register(String, String)  
        – void sendMessage(String, String)  
        – List<String> getHistory()  
        – List<String> getOnlineUsers()  
        – void registerCallback(String, ClientCallback)  
        – void logout(String)

  • ClientCallback.java  
      RMI interface for client callbacks:
        – void receiveMessage(String)

  • ChatServerRMI.java  
      Implements ChatService; extends JFrame.  
      Auto-starts (or attaches to) a local RMI registry on port 1099.  
      Maintains credentials in users.txt.  
      Keeps synchronized `history` and `callbacks` maps.  
      GUI shows “Online Users” and “Chat Log.”  
      Broadcasts join/leave and new messages to all registered callbacks.

  • ChatClientRMI.java  
      Implements ClientCallback; extends UnicastRemoteObject.  
      On startup:
        1) Prompts “Enter server IP:” (default localhost).  
        2) Authenticates via login/register.  
        3) Immediately calls `registerCallback(username, this)` so the server’s GUI “Online Users” updates.  
        4) Fetches and displays all past history with pop-ups suppressed.  
        5) Fetches and displays current online users (excluding itself).  
      Thereafter, any new join/leave or chat message from others triggers a pop-up.

  • users.txt  
      Stores lines of “username:sha256hash.”  
      Initially empty. New “Register” appends to it.

Prerequisites
-------------
  • Java 8 (or newer) installed (javac/java on PATH).  
  • No external libraries required.

How to Compile
--------------
Open a terminal in this folder and run:
    javac ChatService.java ClientCallback.java ChatServerRMI.java ChatClientRMI.java

This creates:
  • ChatService.class  
  • ClientCallback.class  
  • ChatServerRMI.class  
  • ChatClientRMI.class

How to Run
----------
1) Start the server (auto-starts RMI registry on port 1099 if not already running):
       java ChatServerRMI
   – Server GUI appears:
       • Left pane: “Online Users” (automatically updated as clients register/drop).  
       • Center pane: “Chat Log” (all join/leave and messages).  
       • Bottom text field: type text and press Enter to broadcast as “SERVER: …”.

2) Start one or more clients:
       java ChatClientRMI
   – A dialog prompts “Enter server IP:” (type localhost if on the same machine).  
   – Next, a “Login/Register” dialog appears:
       • Provide username/password.  
       • Click “Register” to create a new account (appends to users.txt), or “Login” if it exists.  
   – Once logged in:
       • Client immediately calls `registerCallback` so:
           – The server’s “Online Users” list shows this user right away.  
       • Then the client fetches all past history (no pop-ups for old messages).  
       • The client fetches current online users (excluding itself).  
       • Thereafter, any new join/leave or chat message from another user triggers a pop-up.

3) Multiple clients can connect at once:
   – Each new client sees the full history first (no pop-ups).  
   – All other clients see “SERVER: <user> has joined” once (bubble + pop-up).  
   – When a client sends a chat, others see it immediately (bubble + pop-up).  
   – On closing a client window, `logout(<user>)` is called automatically, and all others see “SERVER: <user> has left.”

Notes / Troubleshooting
-----------------------
• **users.txt**  
  – Must exist (even if empty). The server creates it if missing.  
  – Format: `username:hex-encoded-sha256(password)`. Do not manually edit except to remove accounts.

• **Port 1099**  
  – The server uses TCP 1099 for RMI. Ensure no firewall or other service blocks it.

• **Pop-up behavior**  
  – During initial history load, pop-ups are suppressed. Only truly new messages/join/leave events show pop-ups after login.

• **Logout on close**  
  – Closing the client window triggers `logout(username)`, so the server’s “Online Users” pane stays accurate.

License
-------
Provided as-is for educational use. Modify or extend freely.
