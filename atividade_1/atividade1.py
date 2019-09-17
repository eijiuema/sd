import sys
import time
import socket
import struct
import random
import threading

PROCCESS_N = 3 # Número total de processos
ID = int(sys.argv[1]) # Identificador do processo
MULTICAST_GROUP = '224.3.29.71' # IP do grupo de Multicast
SERVER_ADDRESS = ('', 10000+ID) # IP e porta que o processo vai ouvir

print('Starting proccess {}'.format(ID))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(SERVER_ADDRESS)

group = socket.inet_aton(MULTICAST_GROUP)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(
    socket.IPPROTO_IP,
    socket.IP_ADD_MEMBERSHIP,
    mreq
)

class Mensagem():

    format = 'I100s?I' # Formato da estrutura binária

    def __init__(self, id, texto, ack, timestamp):
        self.id = id # Identificador da mensagem (concatenação da marca de tempo com o id do processo remetente)
        self.texto = texto # Texto da mensagem
        self.ack = ack # Flag de ACK
        self.timestamp = timestamp # Marca de tempo da mensagem (no caso do ACK é referente a mensagem que o ACK confirma)

    def __str__(self):
        return '[id={}, texto={}, ack={}, timestamp={}]'.format(self.id, self.texto, self.ack, self.timestamp)

    def __repr__(self):
        return str(self.texto)

    def pack(self):
        return struct.pack(Mensagem.format, self.id, self.texto.encode('UTF-8'), self.ack, self.timestamp)

    def unpack(data):
        mensagem = struct.unpack(Mensagem.format, data)
        return Mensagem(mensagem[0], mensagem[1].decode('UTF-8').strip('\x00'), mensagem[2], mensagem[3])

timestamp = 0 # Inicialização das marcas de tempo
fila = [] # Inicialização da fila de mensagens
acks = dict() # Inicialização dos contadores de ACKs

# Envia a mensagem para todos os processos
def send(mensagem):
    print('[{}] Enviado {}'.format(timestamp, mensagem))
    for i in range(0, PROCCESS_N):
        sock.sendto(mensagem.pack(), (MULTICAST_GROUP, 10000+i))
        # time.sleep(random.randint(0, 3)) # Dorme um intervalo aleatório (simula atrasos na rede)

# Processa as mensagens recebidas e envia ACKs
def listen():
    global timestamp, fila, acks
    while True:
        data, address = sock.recvfrom(1024) # Aguarda por uma mensagem
        mensagem = Mensagem.unpack(data) # Decodifica a mensagem
        timestamp = max(timestamp, mensagem.timestamp)+1 # Atualiza a marca de tempo (em comparação com a recebida)

        if(mensagem.ack == False): # Caso seja mensagem
            fila.append(mensagem) # Adiciona a mensagem na fila
            fila.sort(key=lambda mensagem: mensagem.id) # Reordena a fila
            send(Mensagem(mensagem.id, '', True, timestamp)) # Envia ACK
        else: # Caso seja ACK
            if(mensagem.id in acks): # Verifica se a contagem de ACKs já existe
                acks[mensagem.id]+= 1 # Incrementa a contagem de ACKs
            else:
                acks[mensagem.id] = 1 # Inicia a contagem de ACKs

        # Processo de remoção da fila
        if(len(fila) > 0):
            if(acks.get(fila[0].id, 0) >= 3):
                acks.pop(fila[0].id)
                fila.pop(0)
        
        print('[{}] Recebido {}'.format(timestamp, mensagem))
        print('[{}] Fila: {}'.format(timestamp, fila))
        print('[{}] Acks: {}'.format(timestamp, acks))
        # time.sleep(random.randint(0, 3)) # Dorme um intervalo aleatório (simula atrasos na rede)

# Envia as mensagens do usuário
def write():
    global timestamp
    while True:
        texto = input('') # Recebe a mensagem do terminal
        timestamp+= 1 # Incrementa a marca de tempo
        send(Mensagem(timestamp*10+ID, texto, False, timestamp)) # Envia a mensagem
        # time.sleep(random.randint(0, 3)) # Dorme um intervalo aleatório (simula atrasos na rede)

listen_thread = threading.Thread(target=listen)
write_thread = threading.Thread(target=write)
listen_thread.daemon = True
write_thread.daemon = True
listen_thread.start()
write_thread.start()

while True:
    time.sleep(1)
