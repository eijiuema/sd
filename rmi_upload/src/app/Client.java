package app;

import java.io.File;
import java.nio.file.Files;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class Client {

    public static void main(String[] args) {
        String host = args[0];
        String filepath = args[1];
        try {
            File file = new File(filepath);
            byte[] content = Files.readAllBytes(file.toPath());
            Registry registry = LocateRegistry.getRegistry(host);
            Upload server = (Upload) registry.lookup("Server");
            server.upload(content, content.length + ".txt");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}