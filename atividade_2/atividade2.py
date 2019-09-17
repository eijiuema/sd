import os
import sys
import socket
import pickle
from time import sleep
from queue import Queue
from threading import Thread

PROCCESS_N = 3
HOST = '127.0.0.1'
PORT = 5000

queues = [Queue()]*PROCCESS_N
clients = [None]*PROCCESS_N

def main():

    for i in range(0, 3):
        Thread(target=t_process, args=[i, queues[i]], daemon=True).start()

    while True:
        id, tempo = input().split()
        id = int(id)
        tempo = int(tempo)
        if 0 <= id < PROCCESS_N:
            queues[id].put(tempo)

def t_process(id, queue):

    log_file = open(f'log_{id}.txt', 'w')

    clock = 0
    # 0 => Não requisitado
    # 1 => Requisitado
    # 2 => Em uso
    recurso = 0

    def log(message):
        log_file.write(f'{clock}: {message}\n')
        log_file.flush()
        os.fsync(log_file.fileno())

    log(f'Iniciando processo com id = {id}')

    def t_listen():
        nonlocal clock
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT + id))
        server.listen(5)
        log(f'Ouvindo na porta = {PORT + id}')
        clients[id] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clients[id].connect((HOST, PORT + id))
        while True:
            client, addr = server.accept()
            log('Cliente conectado')
            while True:
                data = pickle.loads(client.recv(1024))

                if data['clock'][0] > clock:
                    clock = data['clock'][0]

                clock += 1

                if data['message'] == 'request':

                    log(f'Enviado OK ao processo {data["clock"][1]}')
                    if recurso == 0:
                        data = {
                            'clock': (clock, id),
                            'message': 'ok'
                        }
                        client.send(pickle.dumps(data))

                if data['message'] == 'ok':
                    

                log(f'Dados recebidos: {data}')

    Thread(target=t_listen, daemon=True).start()

    while True:
        if not queue.empty():
            tempo = queue.get()
            clock += 1
            for client in clients:
                data = {
                    'clock': (clock, id),
                    'message': 'request'
                }
                client.send(pickle.dumps(data))
        sleep(1)

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt):
        pass