import argparse
import random
from time import sleep
import socket
import pickle

HOST = '127.0.0.1'
PORT = 5000

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--pid', type=int)
    parser.add_argument('--failable', type=bool)
    parser.add_argument('--trigger_election', type=bool)

    args = parser.parse_args()

    process = Process(args.pid)

    while True:
        input()
        sleep(1)


class Process():

    def __init__(self, pid):
        self.pid = pid

    def __del__(self):
        pass

    def ping(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        for i in range(0, 3):

            try:
                s.connect((HOST, PORT+self.pid))
            except socket.error, e:
                

    def election(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if __name__ == "__main__":
    main()
    pass