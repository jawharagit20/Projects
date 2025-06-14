import java.io.*;
import java.net.*;
import java.security.MessageDigest;
import java.util.*;                // Ensures java.util.List is unambiguous
import java.util.concurrent.*;
import javax.swing.*;
import javax.swing.border.*;
import java.awt.*;
import java.awt.event.*;
import javax.net.ssl.*;
import java.security.KeyStore;

public class ChatServer extends JFrame {
    private static final int PORT = 12345;
    private Map<String, String> users = new ConcurrentHashMap<>();
    private File usersFile = new File("users.txt");
    private Set<PrintWriter> clientWriters = ConcurrentHashMap.newKeySet();
    private java.util.List<String> history = Collections.synchronizedList(new ArrayList<>());  
    private ConcurrentHashMap<String, PrintWriter> userToWriter = new ConcurrentHashMap<>();

    private DefaultListModel<String> onlineModel = new DefaultListModel<>();
    private JTextArea logArea = new JTextArea();
    private JTextField adminField = new JTextField();

    public ChatServer() throws Exception {
        super("Chat Server");
        loadUsers();
        setupGUI();
        startServer();
    }

    private void loadUsers() throws Exception {
        if (!usersFile.exists()) {
            usersFile.createNewFile();
        }
        try (BufferedReader br = new BufferedReader(new FileReader(usersFile))) {
            String line;
            while ((line = br.readLine()) != null) {
                String[] parts = line.split(":");
                if (parts.length == 2) {
                    users.put(parts[0], parts[1]);
                }
            }
        }
    }

    private void saveUser(String username, String hashedPassword) throws Exception {
        try (FileWriter fw = new FileWriter(usersFile, true)) {
            fw.write(username + ":" + hashedPassword + "\n");
        }
    }

    private String hash(String password) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] bytes = md.digest(password.getBytes("UTF-8"));
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    private void setupGUI() {
        setSize(800, 600);
        setLayout(new BorderLayout());
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        // Left panel: Online users
        JPanel leftPanel = new JPanel(new BorderLayout());
        leftPanel.setBorder(new CompoundBorder(
            new EmptyBorder(10, 10, 10, 10),
            new TitledBorder("Online Users")));
        JList<String> userList = new JList<>(onlineModel);
        userList.setBackground(new Color(230, 230, 250));
        userList.setFont(new Font("SansSerif", Font.PLAIN, 14));
        leftPanel.add(new JScrollPane(userList), BorderLayout.CENTER);
        leftPanel.setPreferredSize(new Dimension(200, 0));

        // Center panel: Chat log
        JPanel centerPanel = new JPanel(new BorderLayout());
        centerPanel.setBorder(new CompoundBorder(
            new EmptyBorder(10, 10, 10, 10),
            new TitledBorder("Chat Log")));
        logArea.setEditable(false);
        logArea.setFont(new Font("SansSerif", Font.PLAIN, 14));
        logArea.setBackground(Color.WHITE);
        centerPanel.add(new JScrollPane(logArea), BorderLayout.CENTER);

        // Bottom panel: Admin broadcast
        JPanel bottomPanel = new JPanel(new BorderLayout());
        bottomPanel.setBorder(new CompoundBorder(
            new EmptyBorder(10, 10, 10, 10),
            new TitledBorder("Broadcast as Server")));
        adminField.setFont(new Font("SansSerif", Font.PLAIN, 14));
        bottomPanel.add(adminField, BorderLayout.CENTER);
        adminField.addActionListener(e -> {
            String text = adminField.getText().trim();
            if (!text.isEmpty()) {
                String full = "SERVER: " + text;
                history.add(full);
                appendLog(full);
                broadcast(full);
                adminField.setText("");
            }
        });

        add(leftPanel, BorderLayout.WEST);
        add(centerPanel, BorderLayout.CENTER);
        add(bottomPanel, BorderLayout.SOUTH);
        setVisible(true);
    }

    private void appendLog(String message) {
        SwingUtilities.invokeLater(() -> logArea.append(message + "\n"));
    }

    private void updateOnlineListAdd(String user) {
        SwingUtilities.invokeLater(() -> onlineModel.addElement(user));
    }

    private void updateOnlineListRemove(String user) {
        SwingUtilities.invokeLater(() -> onlineModel.removeElement(user));
    }

    private void startServer() {
    new Thread(() -> {
        try {
            // SSL Setup
            KeyStore keyStore = KeyStore.getInstance("JKS");
            keyStore.load(new FileInputStream("server.keystore"), "chatpass".toCharArray());
            
            KeyManagerFactory keyManagerFactory = KeyManagerFactory.getInstance("SunX509");
            keyManagerFactory.init(keyStore, "chatpass".toCharArray());
            
            SSLContext sslContext = SSLContext.getInstance("TLS");
            sslContext.init(keyManagerFactory.getKeyManagers(), null, null);
            
            SSLServerSocketFactory factory = sslContext.getServerSocketFactory();
            SSLServerSocket listener = (SSLServerSocket) factory.createServerSocket(PORT);
            
            appendLog("SSL Server started on port " + PORT);
            while (true) {
                Socket socket = listener.accept();
                new ClientHandler(socket).start();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }).start();
}

    private void broadcast(String message) {
        for (PrintWriter writer : clientWriters) {
            writer.println("MESSAGE " + message);
        }
    }

    private class ClientHandler extends Thread {
        private String username;
        private BufferedReader in;
        private PrintWriter out;

        public ClientHandler(Socket socket) throws Exception {
            in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            out = new PrintWriter(socket.getOutputStream(), true);
        }

        public void run() {
            try {
                // Authentication loop
                while (true) {
                    out.println("SUBMITOPTION");
                    String line = in.readLine();
                    if (line == null) return;
                    if (line.startsWith("REGISTER")) {
                        String[] tokens = line.split(" ", 3);
                        if (tokens.length < 3) {
                            out.println("ERROR Invalid REGISTER");
                            continue;
                        }
                        String user = tokens[1], pass = tokens[2];
                        if (users.containsKey(user)) {
                            out.println("REGISTERFAIL");
                        } else {
                            String hashed = hash(pass);
                            users.put(user, hashed);
                            saveUser(user, hashed);
                            out.println("REGISTERSUCCESS");
                            appendLog("User registered: " + user);
                        }
                    } else if (line.startsWith("LOGIN")) {
                        String[] tokens = line.split(" ", 3);
                        if (tokens.length < 3) {
                            out.println("ERROR Invalid LOGIN");
                            continue;
                        }
                        String user = tokens[1], pass = tokens[2];
                        String hashed = hash(pass);
                        if (hashed.equals(users.get(user))) {
                            username = user;
                            out.println("LOGINSUCCESS");
                            break;
                        } else {
                            out.println("LOGINFAIL");
                        }
                    } else {
                        out.println("ERROR Unknown");
                    }
                }

                // 1) Track the new client
                clientWriters.add(out);
                userToWriter.put(username, out);
                updateOnlineListAdd(username);

                // 2) SEND CHAT HISTORY FIRST (prevents duplicate “has joined”)
                synchronized (history) {
                    for (String msg : history) {
                        out.println("MESSAGE " + msg);
                    }
                }

                // 3) NOW broadcast “has joined” once
                String joinMsg = "SERVER: " + username + " has joined";
                history.add(joinMsg);
                appendLog(joinMsg);
                broadcast(joinMsg);

                // 4) Read further messages from this client
                String message;
                while ((message = in.readLine()) != null) {
                    if (message.startsWith("MESSAGE")) {
                        String text = message.substring(8);
                        String full = username + ": " + text;
                        history.add(full);
                        appendLog(full);
                        broadcast(full);
                    }
                }
            } catch (Exception e) {
                e.printStackTrace();
            } finally {
                if (username != null) {
                    clientWriters.remove(out);
                    userToWriter.remove(username);
                    updateOnlineListRemove(username);

                    String leftMsg = "SERVER: " + username + " has left";
                    history.add(leftMsg);
                    appendLog(leftMsg);
                    broadcast(leftMsg);
                }
                try { in.close(); } catch (IOException e) {}
            }
        }
    }

    public static void main(String[] args) throws Exception {
        new ChatServer();
    }
}

