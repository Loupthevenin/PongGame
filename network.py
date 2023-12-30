import socket


class Network:
    def __init__(self, server, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server
        self.port = port
        self.addr = (self.server, self.port)
        self.id = self.connect()

    def connect(self):
        self.client_socket.connect(self.addr)
        return self.client_socket.recv(2048*1).decode()

    def send(self, data) -> str:
        try:
            self.client_socket.send(str.encode(data))
            reply = self.client_socket.recv(2048*1).decode()
            return reply
        except socket.error as e:
            return str(e)
