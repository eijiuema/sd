import sys
from time import sleep
import socket
import pickle
from threading import Thread

PROCESS_N = 3
ADDRESS = '127.0.0.1'
PORT = 5000

def main():

    pid = int(sys.argv[1])

    process = Process(pid)

    while True:
        duracao = int(input())
        for i in range(0, PROCESS_N):
            process.send(i, 'request')
        sleep(1)

class Process():
    OK = 0
    REQUEST = 1
    USING = 2

    def __init__(self, pid):
        self.pid = pid
        self.clock = 0
        self.state = Process.OK
        Thread(target=self.t_listen, daemon=True).start()

    def t_listen(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((ADDRESS, PORT+self.pid))
        server.listen(5)
        print(f"Listening on port {PORT+self.pid}")
        while True:
            client, addr = server.accept()
            print(f"Connected from {addr}")
            data = pickle.loads(client.recv(1024))

            self.clock = max(self.clock, data['clock'])



            print(data)
            client.close()


    def send(self, target_pid, message):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ADDRESS, PORT+target_pid))
        
        data = {
            'pid': self.pid,
            'clock': self.clock,
            'message': message
        }

        client.send(pickle.dumps(data))

if __name__ == "__main__":
    main()
    pass