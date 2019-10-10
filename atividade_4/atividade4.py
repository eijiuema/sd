import argparse
from time import sleep
from threading import Thread
from threading import Lock
from multiprocessing.connection import Listener
from multiprocessing.connection import Client

ADDRESS = '127.0.0.1'
PORT = 5000

# Threaded function snippet
def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread
    return wrapper

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=int, required=True)
    parser.add_argument("--neighbours", nargs="*", type=int, default=[])
    parser.add_argument("--election", action='store_true')
    parser.add_argument('--capacity', type=int, required=True)
    parser.add_argument('--n', type=int, required=True)
    args = parser.parse_args()
    Process(args.n, args.id, args.neighbours, args.election, ADDRESS, PORT, args.capacity)
    pass

class Process:

    def __init__(self, n : int, id : int, neighbours : int, election : bool, address : str, port : int, capacity : int):
        self.n = n
        self.id = id
        self.address = address
        self.port = port
        self.neighbours = neighbours
        self.parent = None
        self.parent_lock = Lock()
        self.election_id = None
        self.election_id_lock = Lock()
        self.ack_counter = 0
        self.capacity = capacity
        self.max_capacity = (self.id, self.capacity)
        self.listen = self.listen()

        sleep(1)

        if election:
            print('Iniciando eleição')
            with self.election_id_lock:
                with self.parent_lock:
                    self.parent = None
                self.election_id = self.id
                self.ack_counter = 0
                print(f'Enviando pedido de eleição para {self.neighbours}')
                self.send_neighbours({
                    'message': 'election',
                    'election_id': self.election_id
                })

        while(True):
            sleep(1)

    @threaded
    def listen(self):
        with Listener((self.address, self.port+self.id), backlog=self.n*self.n) as listener:
            while True:
                with listener.accept() as conn:
                    data = conn.recv()

                    if data['message'] == 'election':
                        if (self.parent is None and self.election_id is None) or self.election_id < data['election_id']:
                            if self.election_id is not None:
                                print('Eleição de maior prioridade recebida')
                            with self.parent_lock:
                                self.parent = data['sender']
                            with self.election_id_lock:
                                self.election_id = data['election_id']
                            self.ack_counter = 0
                            self.send_neighbours({
                                'message': 'election',
                                'election_id': data['election_id']
                            }, exceptions=[self.parent])
                            print(f"Repassando pedido de eleição de {self.election_id} enviada por {self.parent}")
                        else:
                            print(f"Confirmando pedido de eleição de {data['election_id']} enviada por {data['sender']}")
                            self.send(data['sender'], {
                                'message': 'ack',
                                'capacity': self.max_capacity
                            })
                    elif data['message'] == 'ack':
                        print(f"Guardando confirmação de {data['sender']}")
                        self.ack_counter+= 1
                        if (self.max_capacity[1] < data['capacity'][1]):
                            self.max_capacity = data['capacity']

                        if self.parent is None:
                            if self.ack_counter == len(self.neighbours):
                                self.ack_counter = 0
                                print(f'Fim da eleição, vencedor: {self.max_capacity}')
                                self.send_all({
                                    'message': 'winner',
                                    'leader': self.max_capacity
                                })
                        else:
                            if self.ack_counter == len(self.neighbours) - 1:
                                self.ack_counter = 0
                                print(f"Confirmando pedido de eleição para o nó pai ({self.parent})")
                                self.send(self.parent, {
                                    'message': 'ack',
                                    'capacity': self.max_capacity,
                                })
                    elif data['message'] == 'winner':
                        if (self.max_capacity[1] < data['leader'][1]):
                            self.max_capacity = data['leader']
                        print(f"Vencedor: {self.max_capacity}")

                    conn.close()

    @threaded
    def send(self, target, data):
        try:
            with Client((self.address, self.port+target)) as client:
                data['sender'] = self.id
                client.send(data)
                client.close()
        except ConnectionRefusedError as e:
            print(str(e))
            print("Connection refused")

    def send_neighbours(self, data, exceptions = []):
        for i in [x for x in self.neighbours if x not in exceptions]:
            self.send(i, data)

    def send_all(self, data, exceptions = []):
        for i in [x for x in range(self.n) if x not in exceptions and x != self.id]:
            self.send(i, data)

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt):
        exit(0)
    pass