import socket
import threading
import pickle


class PongServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"Server listening on {self.host}:{self.port}")

        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Accepted connection from {addr}")

            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()
            self.clients.append(client_socket)

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = pickle.loads(data)
                print(f"Received message: {message}")

                # Traiter le message (par exemple, mettre à jour l'état du jeu)

                # Envoyer la mise à jour à tous les clients
                for client in self.clients:
                    client.send(pickle.dumps(message))
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            self.clients.remove(client_socket)
            client_socket.close()


if __name__ == '__main__':
    server = PongServer("127.0.0.1", 5555)
    server.start()
