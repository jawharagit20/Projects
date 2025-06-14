import java.awt.*;
import java.awt.event.*;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.server.UnicastRemoteObject;
import java.util.List;
import javax.swing.*;
import javax.swing.border.*;
import java.text.SimpleDateFormat;
import java.util.Date;

public class ChatClientRMI extends UnicastRemoteObject implements ClientCallback {
    private static final long serialVersionUID = 1L;

    private ChatService server;
    private String username;
    private JFrame frame = new JFrame("Chat Client (RMI - TLS Secured)");
    private DefaultListModel<String> userListModel = new DefaultListModel<>();
    private JList<String> userList = new JList<>(userListModel);
    private JPanel messagePanel = new JPanel();
    private JScrollPane messageScroll;
    private JTextField inputField = new JTextField();

    // Suppress pop-ups while loading old history
    private boolean suppressPopup = false;

    public ChatClientRMI() throws RemoteException {
        // Build the GUI
        frame.setSize(800, 600);
        frame.setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
        frame.setLayout(new BorderLayout());

        // Ensure logout is called when window closes
        frame.addWindowListener(new WindowAdapter() {
            @Override
            public void windowClosing(WindowEvent e) {
                try {
                    if (username != null && server != null) {
                        server.logout(username);
                    }
                } catch (Exception ex) { /* ignore */ }
                frame.dispose();
                System.exit(0);
            }
        });

        // Left panel: Online Users
        JPanel leftPanel = new JPanel(new BorderLayout());
        leftPanel.setBorder(new CompoundBorder(
            new EmptyBorder(10, 10, 10, 10),
            new TitledBorder("Online Users")));
        userList.setBackground(new Color(34, 40, 49));
        userList.setFont(new Font("SansSerif", Font.PLAIN, 14));
        userList.setForeground(Color.WHITE);
        leftPanel.add(new JScrollPane(userList), BorderLayout.CENTER);
        leftPanel.setPreferredSize(new Dimension(200, 0));

        // Right panel: Chat area
        JPanel rightPanel = new JPanel(new BorderLayout());
        rightPanel.setBackground(new Color(29, 33, 41));
        rightPanel.setBorder(new CompoundBorder(
            new EmptyBorder(10, 10, 10, 10),
            new TitledBorder(null, "Chat", TitledBorder.LEADING, TitledBorder.TOP,
                new Font("SansSerif", Font.BOLD, 14), Color.WHITE)));

        // Message display
        messagePanel.setLayout(new BoxLayout(messagePanel, BoxLayout.Y_AXIS));
        messagePanel.setBackground(new Color(29, 33, 41));
        messageScroll = new JScrollPane(messagePanel);
        messageScroll.getViewport().setBackground(new Color(29, 33, 41));
        rightPanel.add(messageScroll, BorderLayout.CENTER);

        // Input area: text field + Send button
        JPanel inputPanel = new JPanel(new BorderLayout());
        inputPanel.setBackground(new Color(29, 33, 41));
        inputPanel.setBorder(new EmptyBorder(10, 0, 0, 0));
        inputField.setPreferredSize(new Dimension(500, 40));
        inputField.setFont(new Font("SansSerif", Font.PLAIN, 14));
        inputField.setBackground(new Color(50, 56, 66));
        inputField.setForeground(Color.WHITE);
        JButton sendButton = new JButton("Send");
        sendButton.setBackground(new Color(40, 167, 69));
        sendButton.setForeground(Color.WHITE);
        sendButton.setFont(new Font("SansSerif", Font.BOLD, 14));
        inputPanel.add(inputField, BorderLayout.CENTER);
        inputPanel.add(sendButton, BorderLayout.EAST);
        rightPanel.add(inputPanel, BorderLayout.SOUTH);

        frame.add(leftPanel, BorderLayout.WEST);
        frame.add(rightPanel, BorderLayout.CENTER);

        // "Send" action
        ActionListener sendAction = e -> {
            String text = inputField.getText().trim();
            if (!text.isEmpty()) {
                try {
                    server.sendMessage(username, text);
                    inputField.setText("");
                } catch (Exception ex) {
                    ex.printStackTrace();
                }
            }
        };
        sendButton.addActionListener(sendAction);
        inputField.addActionListener(sendAction);

        frame.setVisible(true);
    }

    /**
     * Creates a rounded "bubble" containing [sender, text, timestamp].
     */
    private JPanel createBubble(String sender, String text, boolean isSelf) {
        String time = new SimpleDateFormat("HH:mm").format(new Date());
        Color bgColor = isSelf ? new Color(39, 174, 96) : new Color(44, 62, 80);
        Color textColor = new Color(236, 240, 241);
        Color nameColor = new Color(0, 0, 0);
        Color timeColor = new Color(149, 165, 166);

        JPanel bubblePanel = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2 = (Graphics2D) g;
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING,
                                     RenderingHints.VALUE_ANTIALIAS_ON);
                g2.setColor(bgColor);
                g2.fillRoundRect(0, 0, getWidth(), getHeight(), 20, 20);
                super.paintComponent(g);
            }
        };
        bubblePanel.setOpaque(false);
        bubblePanel.setLayout(new BorderLayout());
        bubblePanel.setBorder(new EmptyBorder(5, 5, 5, 5));

        JLabel nameLabel = new JLabel(sender);
        nameLabel.setFont(new Font("SansSerif", Font.BOLD, 12));
        nameLabel.setForeground(nameColor);

        JLabel textLabel = new JLabel("<html><body style=\"width:200px\">" + text + "</body></html>");
        textLabel.setFont(new Font("SansSerif", Font.PLAIN, 14));
        textLabel.setForeground(textColor);

        JLabel timeLabel = new JLabel(time);
        timeLabel.setFont(new Font("SansSerif", Font.PLAIN, 10));
        timeLabel.setForeground(timeColor);

        JPanel contentPanel = new JPanel();
        contentPanel.setOpaque(false);
        contentPanel.setLayout(new BoxLayout(contentPanel, BoxLayout.Y_AXIS));
        contentPanel.add(nameLabel);
        contentPanel.add(Box.createVerticalStrut(5));
        contentPanel.add(textLabel);
        contentPanel.add(Box.createVerticalStrut(5));
        contentPanel.add(timeLabel);

        bubblePanel.add(contentPanel, BorderLayout.CENTER);
        return bubblePanel;
    }

    /**
     * Adds a message bubble to the UI (and scrolls down).
     * Pops up a notification if someone else (≠ you and ≠ "SERVER") sends it,
     * but only if suppressPopup == false.
     */
    private void addMessageBubble(String sender, String text) {
        boolean isSelf = sender.equals(username);
        JPanel bubble = createBubble(sender, text, isSelf);

        JPanel container = new JPanel();
        container.setLayout(new BoxLayout(container, BoxLayout.Y_AXIS));
        container.setOpaque(false);
        if (isSelf) {
            container.setAlignmentX(Component.RIGHT_ALIGNMENT);
        } else {
            container.setAlignmentX(Component.LEFT_ALIGNMENT);
        }
        container.add(bubble);
        container.add(Box.createVerticalStrut(10));

        SwingUtilities.invokeLater(() -> {
            messagePanel.add(container);
            messagePanel.revalidate();
            messageScroll.getVerticalScrollBar().setValue(
                messageScroll.getVerticalScrollBar().getMaximum()
            );
        });

        // Only show pop-up if not suppressing, not self, and not "SERVER"
        if (!suppressPopup && !isSelf && !sender.equals("SERVER")) {
            SwingUtilities.invokeLater(() -> {
                JOptionPane.showMessageDialog(frame,
                    sender + " sent a new message:\n" + text,
                    "New Message",
                    JOptionPane.INFORMATION_MESSAGE);
            });
        }
    }

    private String[] showLoginRegisterDialog() {
        String[] options = { "Login", "Register" };
        int choice = JOptionPane.showOptionDialog(
            frame, "Choose:", "Login/Register",
            JOptionPane.YES_NO_OPTION,
            JOptionPane.QUESTION_MESSAGE,
            null, options, options[0]
        );

        JPanel panel = new JPanel(new GridLayout(2, 2, 5, 5));
        panel.add(new JLabel("Username:"));
        JTextField userField = new JTextField();
        panel.add(userField);
        panel.add(new JLabel("Password:"));
        JPasswordField passField = new JPasswordField();
        panel.add(passField);

        int result = JOptionPane.showConfirmDialog(
            frame, panel, options[choice], JOptionPane.OK_CANCEL_OPTION
        );
        if (result == JOptionPane.OK_OPTION) {
            return new String[] {
                options[choice],
                userField.getText(),
                new String(passField.getPassword())
            };
        }
        return null;
    }

    /**
     * Main flow (correct order):
     * 1) Prompt for server IP (like RPC client)
     * 2) Lookup RMI registry on that host:1099
     * 3) Authenticate (login/register)
     * 4) **Register callback immediately** (so server GUI picks you up right away)
     * 5) Fetch & display old history (suppressing pop-ups)
     * 6) Fetch & display current online users
     */
    public void runClient() {
        String host = null;
        try {
            // TLS/SSL Configuration for client
            System.setProperty("javax.net.ssl.trustStore", "client.jks");
            System.setProperty("javax.net.ssl.trustStorePassword", "clientpass");

            // 1) Prompt for server IP
            host = JOptionPane.showInputDialog(frame, "Enter server IP:", "localhost");
            if (host == null || host.trim().isEmpty()) {
                System.exit(0);
            }

            // 2) Lookup on (host, 1099)
            server = (ChatService) LocateRegistry
                        .getRegistry(host.trim(), 1099)
                        .lookup("ChatService");

            // 3) Authentication loop
            while (true) {
                String[] cred = showLoginRegisterDialog();
                if (cred == null) {
                    System.exit(0);
                }
                if (cred[0].equals("Login")) {
                    username = cred[1];
                    if (server.login(cred[1], cred[2])) {
                        break;
                    } else {
                        JOptionPane.showMessageDialog(frame, "Login failed");
                    }
                } else {
                    if (server.register(cred[1], cred[2])) {
                        JOptionPane.showMessageDialog(
                            frame, "Registration successful. Please log in."
                        );
                    } else {
                        JOptionPane.showMessageDialog(
                            frame, "Registration failed: user exists"
                        );
                    }
                }
            }

            // 4) Register callback immediately
            server.registerCallback(username, this);

            // 5) Fetch and display old chat history (suppress pop-ups)
            suppressPopup = true;
            List<String> hist = server.getHistory();
            for (String msg : hist) {
                int idx = msg.indexOf(": ");
                if (idx != -1) {
                    String sender = msg.substring(0, idx);
                    String text = msg.substring(idx + 2);
                    addMessageBubble(sender, text);
                }
            }
            suppressPopup = false;

            // 6) Fetch & display current online users (excluding yourself)
            List<String> online = server.getOnlineUsers();
            for (String user : online) {
                if (!user.equals(username)) {
                    userListModel.addElement(user);
                }
            }

        } catch (Exception e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(frame,
                "Could not connect to \"" + host + ":1099\".\nMake sure ChatServerRMI is running.",
                "Connection Error", JOptionPane.ERROR_MESSAGE);
            System.exit(1);
        }
    }

    @Override
    public void receiveMessage(String message) throws RemoteException {
        // Called by server whenever anyone joins, leaves, or sends new chat
        if (message.startsWith("SERVER: ") && message.contains(" has joined")) {
            String user = message.substring("SERVER: ".length(), message.indexOf(" has joined"));
            if (!user.equals(username)) {
                SwingUtilities.invokeLater(() -> userListModel.addElement(user));
            }
            addMessageBubble("SERVER", message.substring("SERVER: ".length()));
        }
        else if (message.startsWith("SERVER: ") && message.contains(" has left")) {
            String user = message.substring("SERVER: ".length(), message.indexOf(" has left"));
            if (!user.equals(username)) {
                SwingUtilities.invokeLater(() -> userListModel.removeElement(user));
            }
            addMessageBubble("SERVER", message.substring("SERVER: ".length()));
        }
        else {
            int idx = message.indexOf(": ");
            if (idx != -1) {
                String sender = message.substring(0, idx);
                String text = message.substring(idx + 2);
                addMessageBubble(sender, text);
            }
        }
    }

    public static void main(String[] args) throws Exception {
        ChatClientRMI client = new ChatClientRMI();
        client.runClient();
    }
}
