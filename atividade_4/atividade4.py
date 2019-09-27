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
    args = parser.parse_args()
    Process(args.id, args.neighbours, args.election, ADDRESS, PORT)
    pass

class Process:

    def __init__(self, id : int, neighbours : int, election : bool, address : str, port : int):
        self.id = id
        self.address = address
        self.port = port
        self.neighbours = neighbours
        self.parent = None
        self.election_id = None
        self.election_id_lock = Lock()
        self.ack_counter = 0
        self.listen = self.listen()

        if election:
            print('Iniciando eleição')
            with self.election_id_lock:
                self.election_id = self.id
                self.ack_counter = 0
                print(f'Enviando pedido de eleição para {self.neighbours}')
                self.send_all({
                    'message': 'election',
                    'election_id': self.election_id
                })

        while(True):
            sleep(1)

    @threaded
    def listen(self):
        with Listener((self.address, self.port+self.id)) as listener:
            while True:
                with listener.accept() as conn:
                    data = conn.recv()

                    if data['message'] == 'election':
                        if self.parent is None and self.election_id is None or self.election_id < data['election_id']:
                            if self.election_id is not None:
                                print('Eleição de maior prioridade recebida')
                            self.parent = data['sender']
                            with self.election_id_lock:
                                self.election_id = data['election_id']
                            self.ack_counter = 0
                            self.send_all({
                                'message': 'election',
                                'election_id': data['election_id']
                            }, exceptions=[self.parent])
                            print(f"Repassando pedido de eleição de {self.election_id} enviada por {self.parent}")
                        else:
                            print(f"Confirmando pedido de eleição de {data['election_id']} enviada por {data['sender']}")
                            self.send(data['sender'], {
                                'message': 'ack'
                            })
                    elif data['message'] == 'ack':
                        print(f"Guardando confirmação de {data['sender']}")
                        self.ack_counter+= 1

                    if self.parent is None:
                        if self.ack_counter == len(self.neighbours):
                            self.ack_counter = 0
                            print(f'Fim da eleição, vencedor: {self.election_id}')
                    else:
                        if self.ack_counter == len(self.neighbours) - 1:
                            print(f"Confirmando pedido de eleição para o nó pai ({self.parent})")
                            self.send(self.parent, {
                                'message': 'ack'
                            })

                    conn.close()

    @threaded
    def send(self, target, data):
        try:
            with Client((self.address, self.port+target)) as client:
                data['sender'] = self.id
                client.send(data)
                client.close()
        except ConnectionRefusedError:
            print("Connection refused")

    def send_all(self, data, exceptions = []):
        for i in [x for x in self.neighbours if x not in exceptions]:
            self.send(i, data)

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt):
        exit(0)
    pass