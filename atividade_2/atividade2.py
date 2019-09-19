import os
import socket
import pickle
import random
import argparse
from time import sleep
from threading import Thread

PROCESS_N = 3
ADDRESS = '127.0.0.1'
PORT = 5000

def main():

    os.system("mode con cols=80 lines=2")

    parser = argparse.ArgumentParser(description="Algoritmo distribuído de exclusão mútua.")
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--sleep_time', type=int, required=True)
    parser.add_argument('--use_time', type=int, required=True)

    args = parser.parse_args()

    Process(args.pid, args.use_time, args.sleep_time)

    while True:
        sleep(1)

class Process():
    OK = 'Não aguardando recurso'
    REQUEST = 'Aguardando recurso'
    USING = 'Utilizando recurso'

    def __init__(self, pid, use_time, sleep_time):
        self.pid = pid
        self.clock = 0
        self.state = Process.OK
        self.request_timestamp = 0
        self.queue = []
        self.ok_count = 0
        self.use_time = use_time
        self.sleep_time = sleep_time
        Thread(target=self._t_listen, daemon=True).start()

        self.set_state(Process.OK)

        while True:

            sleep(self.sleep_time)

            self.clock += 1
            
            if self.state == Process.OK:
                self.set_state(Process.REQUEST)

            self.print_state()

    def log(self, message):
        print(f'{self.clock}: {message}')

    def _t_recurso(self):
        sleep(self.use_time)
        self.set_state(Process.OK)

    def print_state(self):
        os.system('cls')
        print(f'{self.clock}: {self.state}')

    def set_state(self, state):
        self.state = state

        if self.state == Process.OK:
            for pid in self.queue:
                self._send(pid, 'ok')
            self.queue.clear()
            # self.log("Estado: Não usando recurso")
        elif self.state == Process.REQUEST:
            self.request_timestamp = self.clock
            self._send_all('request')
            # self.log("Estado: Aguardando recurso")
        elif self.state == Process.USING:
            self.ok_count = 0
            Thread(target=self._t_recurso).start()
            # self.log("Estado: Usando recurso")

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
                # self.log(f'Ok de {data["pid"]}')
                self.ok_count += 1
                if self.ok_count == PROCESS_N - 1:
                    self.set_state(Process.USING)
            elif data['message'] == 'request':
                # self.log(f'Request de {data["pid"]}')
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
                # self.log(f'Deny de {data["pid"]}')
                pass

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