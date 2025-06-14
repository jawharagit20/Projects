import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.net.*;
import javax.swing.*;
import javax.swing.border.*;
import java.text.SimpleDateFormat;
import java.util.Date;
import javax.net.ssl.*;
import java.security.cert.X509Certificate;
public class ChatClient {
    private BufferedReader in;
    private PrintWriter out;
    private JFrame frame = new JFrame("Chat Client");
    private DefaultListModel<String> userListModel = new DefaultListModel<>();
    private JList<String> userList = new JList<>(userListModel);
    private JPanel messagePanel = new JPanel();
    private JScrollPane messageScroll;
    private JTextField inputField = new JTextField();
    private String username;

    // NEW: flag to suppress pop-ups while loading history
    private boolean initialLoad = true;
    private boolean suppressPopup = false;

    public ChatClient() {
        frame.setSize(800, 600);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new BorderLayout());

        // Left panel: Online users
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

        // Input area
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

        // Send action
        ActionListener sendAction = e -> {
            String text = inputField.getText().trim();
            if (!text.isEmpty()) {
                out.println("MESSAGE " + text);
                inputField.setText("");
            }
        };
        sendButton.addActionListener(sendAction);
        inputField.addActionListener(sendAction);

        frame.setVisible(true);
    }

    // Creates a rounded “bubble” for each message
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

    // Adds a message bubble and (if appropriate) shows a notification pop-up
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

        // NEW: only show pop-up if not suppressing and not from SERVER
        if (!suppressPopup && !isSelf && !sender.equals("SERVER")) {
            SwingUtilities.invokeLater(() -> {
                JOptionPane.showMessageDialog(frame,
                    sender + " sent a new message:\n" + text,
                    "New Message",
                    JOptionPane.INFORMATION_MESSAGE);
            });
        }
    }

    // Shows the login/register dialog
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

    // Main client flow: connect, login/register, then start reading lines
    public void runClient() throws IOException {
        String serverAddress = JOptionPane.showInputDialog(frame, "Enter server IP:", "localhost");
        if (serverAddress == null) {
            System.exit(0);
        }
        Socket socket;
try {
    // SSL Setup - trust all certificates (for development)
    SSLContext sslContext = SSLContext.getInstance("TLS");
    sslContext.init(null, new TrustManager[] {
        new X509TrustManager() {
            public X509Certificate[] getAcceptedIssuers() { return null; }
            public void checkClientTrusted(X509Certificate[] certs, String authType) {}
            public void checkServerTrusted(X509Certificate[] certs, String authType) {}
        }
    }, null);

    SSLSocketFactory factory = sslContext.getSocketFactory();
    socket = factory.createSocket(serverAddress, 12345);
} catch (Exception e) {
    throw new IOException("SSL setup failed", e);
}
        in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        out = new PrintWriter(socket.getOutputStream(), true);

        // Authentication loop
        while (true) {
            String serverMsg = in.readLine();
            if (serverMsg == null) {
                socket.close();
                return;
            }
            if (serverMsg.startsWith("SUBMITOPTION")) {
                String[] cred = showLoginRegisterDialog();
                if (cred == null) {
                    socket.close();
                    return;
                }
                if (cred[0].equals("Login")) {
                    username = cred[1];
                    out.println("LOGIN " + cred[1] + " " + cred[2]);
                } else {
                    out.println("REGISTER " + cred[1] + " " + cred[2]);
                }
            } else if (serverMsg.startsWith("LOGINSUCCESS")) {
                addMessageBubble("SERVER", "Logged in successfully");
                break;
            } else if (serverMsg.startsWith("LOGINFAIL")) {
                JOptionPane.showMessageDialog(frame, "Login failed");
            } else if (serverMsg.startsWith("REGISTERSUCCESS")) {
                JOptionPane.showMessageDialog(frame, "Registration successful. Please log in.");
            } else if (serverMsg.startsWith("REGISTERFAIL")) {
                JOptionPane.showMessageDialog(frame, "Registration failed: user exists.");
            }
        }

        // Start reader thread for any "MESSAGE ..." lines (history + new)
        new Thread(() -> {
            try {
                String line;
                while ((line = in.readLine()) != null) {
                    if (line.startsWith("MESSAGE")) {
                        String msg = line.substring(8);

                        // 1) If it's the join-broadcast for *this* user, that signals end of initial history.
                        if (msg.startsWith("SERVER: " + username + " has joined")) {
                            // Before showing, suppress popups just for this one
                            suppressPopup = true;
                            addMessageBubble("SERVER", msg.substring("SERVER: ".length()));
                            suppressPopup = false;

                            // Now initial load is complete
                            initialLoad = false;
                            continue;
                        }

                        // 2) If we're still in initialLoad (old history), suppress pop-ups
                        if (initialLoad) {
                            suppressPopup = true;
                        }

                        // Handle join/leave and normal messages
                        if (msg.startsWith("SERVER: ") && msg.contains(" has joined")) {
                            String user = msg.substring("SERVER: ".length(), msg.indexOf(" has joined"));
                            if (!user.equals(username)) {
                                userListModel.addElement(user);
                            }
                            addMessageBubble("SERVER", msg.substring("SERVER: ".length()));
                        }
                        else if (msg.startsWith("SERVER: ") && msg.contains(" has left")) {
                            String user = msg.substring("SERVER: ".length(), msg.indexOf(" has left"));
                            if (!user.equals(username)) {
                                userListModel.removeElement(user);
                            }
                            addMessageBubble("SERVER", msg.substring("SERVER: ".length()));
                        }
                        else {
                            int idx = msg.indexOf(": ");
                            if (idx != -1) {
                                String sender = msg.substring(0, idx);
                                String text = msg.substring(idx + 2);
                                addMessageBubble(sender, text);
                            }
                        }

                        // 3) After processing one line of history (if any), restore pop-up behavior
                        if (initialLoad) {
                            suppressPopup = false;
                        }
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }).start();
    }

    public static void main(String[] args) throws Exception {
        ChatClient client = new ChatClient();
        client.runClient();
    }
}

