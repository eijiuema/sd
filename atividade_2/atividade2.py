import os
import sys
import socket
import pickle
import random
from time import sleep
from threading import Thread

PROCESS_N = 3
ADDRESS = '127.0.0.1'
PORT = 5000

def main():

    pid = int(sys.argv[1])

    process = Process(pid)

    while True:
        input()

        process.clock += 1

        if process.state == Process.OK:
            process.set_state(Process.REQUEST)
        elif process.state == Process.USING:
            process.set_state(Process.OK)

        sleep(1)

class Process():
    OK = 0
    REQUEST = 1
    USING = 2

    def __init__(self, pid):
        self.pid = pid
        self.clock = 0
        self.state = Process.OK
        self.request_time = 0
        self.queue = []
        self.ok_count = 0
        Thread(target=self._t_listen, daemon=True).start()

    def log(self, message):
        print(f'{self.clock}: {message}')

    def set_state(self, state):
        self.state = state

        if self.state == Process.OK:
            self.file.close()
            for pid in self.queue:
                self._send(pid, 'ok')
            self.queue.clear()
            self.log("Estado: OK")
        elif self.state == Process.REQUEST:
            self.request_time = self.clock
            self._send_all('request')
            self.log("Estado: Aguardando")
        elif self.state == Process.USING:
            self.ok_count = 0
            self.file = open('recurso.txt', 'w')
            self.file.write(f'Processo {self.pid}')
            self.file.flush()
            os.fsync(self.file.fileno())
            self.log("Estado: Usando recurso")

    def _t_listen(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((ADDRESS, PORT+self.pid))
        server.listen(5)
        self.log(f"Listening on port {PORT+self.pid}")
        while True:
            client, addr = server.accept()
            data = pickle.loads(client.recv(1024))
            client.close()

            self.clock = max(self.clock, data['clock']) + 1

            if data['message'] == 'ok':
                self.log(f'Ok de {data["pid"]}')
                self.ok_count += 1
                if self.ok_count == PROCESS_N - 1:
                    self.set_state(Process.USING)
            elif data['message'] == 'request':
                self.log(f'Request de {data["pid"]}')
                if self.state == Process.OK:
                    self._send(data['pid'], 'ok')
                elif self.state == Process.USING:
                    self.queue.append(data['pid'])
                    self._send(data['pid'], 'deny')
                elif self.state == Process.REQUEST:
                    if self.request_time < data['clock']:
                        self.queue.append(data['pid'])
                        self._send(data['pid'], 'deny')
                    elif self.request_time == data['clock']:
                        if self.pid < data['pid']:
                            self.queue.append(data['pid'])
                            self._send(data['pid'], 'deny')
                        else:
                            self._send(data['pid'], 'ok')
                    else:
                        self._send(data['pid'], 'ok')
            elif data['message'] == 'deny':
                self.log(f'Deny de {data["pid"]}')

    def _send(self, target_pid, message):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ADDRESS, PORT+target_pid))
        
        data = {
            'pid': self.pid,
            'clock': self.clock,
            'message': message
        }

        # sleep(random.randint(0, 2))

        client.send(pickle.dumps(data))

    def _send_all(self, message):
        for i in range(0, PROCESS_N):
            if i != self.pid:
                self._send(i, message)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt):
        exit(0)
    pass