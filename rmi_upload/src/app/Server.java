package app;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;

public class Server implements Upload {

    @Override
    public void upload(byte[] data, String serverPath) throws RemoteException {
        try {
            File file = new File("uploaded/" + serverPath);
            FileOutputStream out = new FileOutputStream(file);
            out.write(data);
            out.flush();
            out.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        try {
            Registry registry = LocateRegistry.getRegistry();
            registry.bind("Server", UnicastRemoteObject.exportObject(new Server(), 0));
            System.out.println("Server is ready!");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
}