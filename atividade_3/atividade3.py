import os
import socket
import pickle
import random
import argparse
from time import sleep
from threading import Thread
from threading import Lock

# Threaded function snippet
def threaded(fn):
    """To use as decorator to make a function call threaded.
    Needs import
    from threading import Thread"""
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

PROCESS_N = 5
ADDRESS = '127.0.0.1'
PORT = 5000


def main():

    global PROCESS_N

    # os.system("mode con cols=40 lines=5")

    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=int, required=True)
    parser.add_argument('--n', type=int, required=True)

    args = parser.parse_args()

    PROCESS_N = args.n

    Process(args.id)

    while True:
        sleep(1)


class Process():

    def __init__(self, id):
        self.id = id
        self.clock = 0
        self.clock_lock = Lock()
        self.leader = None
        self.alive_list = [x for x in range(PROCESS_N)]
        # 0 => Não acontecendo
        # 1 => Acontecendo e o processo deve responder
        # 2 => Acontecendo e o processo não deve responder
        self.election_state = 0

        Thread(target=self.t_listen, daemon=True).start()

        self.send_all('ping')
        sleep(2)

        while True:
            with self.clock_lock:
                self.clock += 1
            if self.leader != self.id and self.leader not in self.alive_list:
                if self.election_state == 0:
                    self.start_election()
                else:
                    sleep(5)
                    if self.leader != self.id and self.leader not in self.alive_list:
                        self.start_election()
            self.send_all('ping')
            sleep(1)

    def t_listen(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((ADDRESS, PORT+self.id))
        server.listen(PROCESS_N*PROCESS_N-1)
        while True:
            client = server.accept()[0]
            data = pickle.loads(client.recv(2048))
            client.close()
            with self.clock_lock:
                self.clock = max(self.clock, data['clock']) + 1

            if data['message'] == 'ping' and data['id'] not in self.alive_list:
                self.alive_list.append(data['id'])
                self.print(f"Processo {data['id']} se recuperou")

            if data['message'] == 'alive' and data['id'] > self.id and self.election_state == 1:
                self.election_state = 2
                self.print(f"Processo {data['id']} respondeu, desistindo da eleição...")
                pass

            if data['message'] == 'coordinator' and data['id'] != self.leader:
                self.leader = data['id']
                self.election_state = 0
                self.print(f"Novo líder: {self.leader}")
                pass

            if data['message'] == 'election' and data['id'] < self.id and self.election_state != 2:
                self.print(f"Processo {data['id']} pediu por uma eleição")
                self.send(data['id'], 'alive')
                if self.election_state == 0:
                    self.start_election()
                pass

    @threaded
    def send(self, target, message):
        if target == self.id:
            return

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)

        try:
            s.connect((ADDRESS, PORT+target))
            data = {
                'id': self.id,
                'clock': self.clock,
                'message': message
            }

            s.sendall(pickle.dumps(data))
            s.close()
        except socket.error:
            self.print(f"Falha ao comunicar com o processo {target}")
            if target in self.alive_list:
                self.alive_list.remove(target)
                if target == self.leader:
                    self.print(f"Líder caiu.")

    def send_above(self, message):
        for i in [x for x in self.alive_list if x > self.id]:
            self.send(i, message)

    def send_all(self, message):
        for i in self.alive_list:
            self.send(i, message)

    def start_election(self):
        self.election_state = 1
        if all(i <= self.id for i in self.alive_list):
            self.leader = self.id
            self.print("Líder autoproclamado")
            self.send_all('coordinator')
            self.election_state = 0
        else:
            self.print("Iniciando eleição...")
            self.print("Pedido de eleição enviado")
            self.send_above('election')

    def print(self, msg):
        print(f"[{self.clock}] {msg}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt):
        exit(0)
    pass