import socket
import threading
import pickle


class PongClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        print("Connected to server")

        # Démarrer un thread pour recevoir les mises à jour du serveur
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

    def receive_messages(self):
        try:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                message = pickle.loads(data)
                print(f"Received message: {message}")

                # Traiter la mise à jour de l'état du jeu (par exemple, dessiner les raquettes et la balle)

        except Exception as e:
            print(f"Error receiving messages: {e}")
        finally:
            self.client_socket.close()

    def send_message(self, message):
        self.client_socket.send(pickle.dumps(message))


if __name__ == '__main__':
    client = PongClient("127.0.0.1", 5555)
    client.connect()

    # Le message
    update_data = {"type": "update", "data": {"paddle_A_y": 100, "paddle_B_y": 200, "ball_pos": (300, 400)}}
    client.send_message(update_data)
