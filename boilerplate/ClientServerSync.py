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
    parser.add_argument('--n', type=int, required=True)
    args = parser.parse_args()
    Process(args.id, args.n, ADDRESS, PORT)
    pass

class Process:

    def __init__(self, id : int, n : int, address : str, port : int):
        self.id = id
        self.address = address
        self.port = port
        self.n = n

        self.clock = 0
        self.clock_lock = Lock()

        self.listen = self.listen()

        while(True):
            with self.clock_lock:
                self.clock += 1
            self.send_all('ping')
            sleep(1)

    @threaded
    def listen(self):
        with Listener((self.address, self.port+self.id)) as listener:
            while True:
                with listener.accept() as conn:
                    data = conn.recv()
                    with self.clock_lock:
                        self.clock = max(data['clock'], self.clock) + 1
                    print(f"{self.clock} {data['content']}")
                    conn.close()

    @threaded
    def send(self, target, content):
        try:
            with Client((self.address, self.port+target)) as client:
                client.send({
                    'sender': self.id,
                    'clock': self.clock,
                    'content': content
                })
                client.close()
        except ConnectionRefusedError:
            print("Connection refused")

    def send_all(self, content, exceptions = []):
        for i in [x for x in range(self.n) if x not in exceptions]:
            self.send(i, content)

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt):
        exit(0)
    pass