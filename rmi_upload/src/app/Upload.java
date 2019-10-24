package app;

import java.rmi.Remote;
import java.rmi.RemoteException;

public interface Upload extends Remote {
    public void upload(byte[] data, String serverPath) throws RemoteException;
}