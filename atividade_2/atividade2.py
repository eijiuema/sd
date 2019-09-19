import os
import socket
import pickle
import random
import argparse
from time import sleep
from threading import Thread
from threading import Lock

PROCESS_N = 3
ADDRESS = '127.0.0.1'
PORT = 5000

def main():

    os.system(f"mode con cols=62 lines={PROCESS_N+1}")

    processes = []

    for i in range(0, PROCESS_N):
        processes.append(Process(i, 1, 1))

    while True:
        os.system('cls')
        for process in processes:
            print(f'PID: {process.pid} \tCLOCK: {process.clock} \tSTATE: {process.state}')
            pass
        sleep(0.1)

class Process():
    OK = 'Não aguardando recurso'
    REQUEST = 'Aguardando recurso'
    USING = 'Utilizando recurso\t<===='

    def __init__(self, pid, use_time, sleep_time):
        self.pid = pid
        self.clock = 0
        self.state = Process.OK
        self.request_timestamp = 0
        self.queue = []
        self.ok_count = 0
        self.use_time = use_time
        self.sleep_time = sleep_time
        self.lock = Lock()
        self.set_state(Process.OK)
        
        Thread(target=self._t_start, daemon=True).start()

    def _t_start(self):
        Thread(target=self._t_listen, daemon=True).start()
        Thread(target=self._t_write, daemon=True).start()

    def log(self, message):
        print(f'{message}')

    def _t_recurso(self):
        sleep(self.use_time)
        self.set_state(Process.OK)

    def set_state(self, state):

        with self.lock:
            self.state = state
            if self.state == Process.OK:
                for pid in self.queue:
                    self._send(pid, 'ok')
                self.queue.clear()
            elif self.state == Process.REQUEST:
                self.request_timestamp = self.clock
                self._send_all('request')
            elif self.state == Process.USING:
                self.ok_count = 0
                Thread(target=self._t_recurso).start()

    def _t_write(self):
        while True:

            sleep(self.sleep_time)

            with self.lock:
                self.clock += 1

            if self.state == Process.OK:
                self.set_state(Process.REQUEST)

    def _t_listen(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((ADDRESS, PORT+self.pid))
        server.listen(PROCESS_N*PROCESS_N)
        # self.log(f"Listening on port {PORT+self.pid}")
        while True:
            client, addr = server.accept()
            data = pickle.loads(client.recv(1024))
            client.close()

            with self.lock:
                self.clock = max(self.clock, data['clock']) + 1

            if data['message'] == 'ok':
                # self.log(f'{self.pid}: Ok de {data["pid"]}')
                self.ok_count += 1
                if self.ok_count == PROCESS_N - 1:
                    self.set_state(Process.USING)
            elif data['message'] == 'request':
                # self.log(f'{self.pid}: Request de {data["pid"]}')
                if self.state == Process.OK:
                    self._send(data['pid'], 'ok')
                elif self.state == Process.USING:
                    self.queue.append(data['pid'])
                    self._send(data['pid'], 'deny')
                elif self.state == Process.REQUEST:
                    if self.request_timestamp < data['clock']:
                        self.queue.append(data['pid'])
                        self._send(data['pid'], 'deny')
                    elif self.request_timestamp == data['clock']:
                        if self.pid < data['pid']:
                            self.queue.append(data['pid'])
                            self._send(data['pid'], 'deny')
                        else:
                            self._send(data['pid'], 'ok')
                    else:
                        self._send(data['pid'], 'ok')
            elif data['message'] == 'deny':
                # self.log(f'{self.pid}: Deny de {data["pid"]}')
                pass

    def _send(self, target_pid, message):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ADDRESS, PORT+target_pid))
        
        data = {
            'pid': self.pid,
            'clock': self.clock,
            'message': message
        }

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