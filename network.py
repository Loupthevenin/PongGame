import socket
import json


class Network:
    def __init__(self, server, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server
        self.port = port
        self.addr = (self.server, self.port)
        self.id = self.connect()
    def connect(self):
        self.client_socket.connect(self.addr)
        return int(self.client_socket.recv(1024*4).decode("utf-8"))

    def close(self):
        self.client_socket.close()

    def send(self, data):
        try:
            self.client_socket.sendall(json.dumps(data).encode("utf-8"))
            reply = self.client_socket.recv(1024*4).decode("utf-8")
            reply_dict = json.loads(reply)
            return reply_dict
        except socket.error as e:
            return str(e)
