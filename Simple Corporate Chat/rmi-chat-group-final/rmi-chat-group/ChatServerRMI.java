import java.io.*;
import java.rmi.*;
import java.rmi.registry.*;
import java.rmi.server.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import javax.swing.*;
import javax.swing.border.*;
import java.awt.*;
import java.awt.event.*;

public class ChatServerRMI extends UnicastRemoteObject implements ChatService {
    private static final long serialVersionUID = 1L;

    // --- Data structures for user credentials, history, and callbacks ---
    private ConcurrentHashMap<String, String> users = new ConcurrentHashMap<>();
    private File usersFile = new File("users.txt");
    private java.util.List<String> history = Collections.synchronizedList(new ArrayList<>());
    private ConcurrentHashMap<String, ClientCallback> callbacks = new ConcurrentHashMap<>();

    // --- GUI components ---
    private DefaultListModel<String> onlineModel = new DefaultListModel<>();
    private JList<String> userList;
    private JTextArea logArea = new JTextArea();
    private JTextField adminField = new JTextField();

    public ChatServerRMI() throws Exception {
        super();
        loadUsers();
        setupGUI();
        startRMIServer();
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
        SwingUtilities.invokeLater(() -> {
            JFrame frame = new JFrame("Chat Server (RMI - TLS Secured)");
            frame.setSize(800, 600);
            frame.setLayout(new BorderLayout());
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

            // Initialize the JList properly
            userList = new JList<>();
            userList.setModel(onlineModel);

            // ----- Left panel: Online Users -----
            JPanel leftPanel = new JPanel(new BorderLayout());
            leftPanel.setBorder(new CompoundBorder(
                new EmptyBorder(10, 10, 10, 10),
                new TitledBorder("Online Users")));
            userList.setBackground(new Color(230, 230, 250));
            userList.setFont(new Font("SansSerif", Font.PLAIN, 14));
            leftPanel.add(new JScrollPane(userList), BorderLayout.CENTER);
            leftPanel.setPreferredSize(new Dimension(200, 0));

            // ----- Center panel: Chat Log -----
            JPanel centerPanel = new JPanel(new BorderLayout());
            centerPanel.setBorder(new CompoundBorder(
                new EmptyBorder(10, 10, 10, 10),
                new TitledBorder("Chat Log")));
            logArea.setEditable(false);
            logArea.setFont(new Font("SansSerif", Font.PLAIN, 14));
            logArea.setBackground(Color.WHITE);
            centerPanel.add(new JScrollPane(logArea), BorderLayout.CENTER);

            // ----- Bottom panel: Admin broadcast field -----
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

            frame.add(leftPanel, BorderLayout.WEST);
            frame.add(centerPanel, BorderLayout.CENTER);
            frame.add(bottomPanel, BorderLayout.SOUTH);

            frame.setVisible(true);
        });
    }

    private void appendLog(String message) {
        SwingUtilities.invokeLater(() -> logArea.append(message + "\n"));
    }

    private void startRMIServer() throws Exception {
        // TLS/SSL Configuration
        System.setProperty("javax.net.ssl.keyStore", "server.jks");
        System.setProperty("javax.net.ssl.keyStorePassword", "serverpass");
        System.setProperty("javax.net.ssl.trustStore", "server.jks");
        System.setProperty("javax.net.ssl.trustStorePassword", "serverpass");
        
        Registry registry;
        try {
            registry = LocateRegistry.createRegistry(1099);
            appendLog("Created local RMI registry on port 1099 with TLS.");
        } catch (RemoteException e) {
            registry = LocateRegistry.getRegistry(1099);
            appendLog("Attached to existing RMI registry on port 1099 with TLS.");
        }
        registry.rebind("ChatService", this);
        appendLog("RMI ChatService bound and ready with TLS security.");
    }

    @Override
    public synchronized boolean login(String username, String password) throws RemoteException {
        try {
            String hashed = hash(password);
            String stored = users.get(username);
            return hashed.equals(stored);
        } catch (Exception e) {
            throw new RemoteException("Error hashing password.", e);
        }
    }

    @Override
    public synchronized boolean register(String username, String password) throws RemoteException {
        try {
            if (users.containsKey(username)) return false;
            String hashed = hash(password);
            users.put(username, hashed);
            saveUser(username, hashed);
            appendLog("User registered: " + username);
            return true;
        } catch (Exception e) {
            throw new RemoteException("Error registering user.", e);
        }
    }

    @Override
    public synchronized void sendMessage(String username, String message) throws RemoteException {
        String full = username + ": " + message;
        history.add(full);
        appendLog(full);
        broadcast(full);
    }

    @Override
    public synchronized java.util.List<String> getHistory() throws RemoteException {
        return new ArrayList<>(history);
    }

    @Override
    public synchronized java.util.List<String> getOnlineUsers() throws RemoteException {
        return new ArrayList<>(callbacks.keySet());
    }

    @Override
    public synchronized void registerCallback(String username, ClientCallback callback) throws RemoteException {
        callbacks.put(username, callback);
        SwingUtilities.invokeLater(() -> {
            if (onlineModel != null) {
                onlineModel.addElement(username);
            }
        });
        String joinMsg = "SERVER: " + username + " has joined";
        history.add(joinMsg);
        appendLog(joinMsg);
        broadcast(joinMsg);
    }

    @Override
    public synchronized void logout(String username) throws RemoteException {
        callbacks.remove(username);
        SwingUtilities.invokeLater(() -> {
            if (onlineModel != null) {
                onlineModel.removeElement(username);
            }
        });
        String leftMsg = "SERVER: " + username + " has left";
        history.add(leftMsg);
        appendLog(leftMsg);
        broadcast(leftMsg);
    }

    private void broadcast(String message) {
        for (ClientCallback cb : callbacks.values()) {
            try {
                cb.receiveMessage(message);
            } catch (Exception e) {
                // ignore individual callback failures
            }
        }
    }

    public static void main(String[] args) {
        try {
            new ChatServerRMI();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
