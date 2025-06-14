import java.io.IOException;
import java.util.List;

public interface ChatProtocol {
    boolean login(String username, String password) throws IOException;
    boolean register(String username, String password) throws IOException;
    void broadcast(String message) throws IOException;
    List<String> getHistory() throws IOException;
}
