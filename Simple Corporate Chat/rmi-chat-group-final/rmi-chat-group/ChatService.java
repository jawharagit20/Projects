import java.rmi.Remote;
import java.rmi.RemoteException;
import java.util.List;

public interface ChatService extends Remote {
    boolean login(String username, String password) throws RemoteException;
    boolean register(String username, String password) throws RemoteException;
    void sendMessage(String username, String message) throws RemoteException;
    List<String> getHistory() throws RemoteException;
    List<String> getOnlineUsers() throws RemoteException;
    void registerCallback(String username, ClientCallback callback) throws RemoteException;
    void logout(String username) throws RemoteException;
}
