import socket
import threading
import pickle
from game import Ponggame, Paddle, Ball
from utils import *


class PongServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []

        # pygame set up
        self.game = Ponggame(round_point)
        self.paddle_A = Paddle(color=color_paddle, left=left_A, top=top_A, move_up=pygame.K_z, move_down=pygame.K_s)
        self.paddle_B = Paddle(color=color_paddle, left=left_B, top=top_B, move_up=pygame.K_UP, move_down=pygame.K_DOWN)
        self.ball = Ball(color=color_ball, rad=rad, speed=speed)

        self.paddle_A_y = height / 2 - self.paddle_A.height / 2
        self.paddle_B_y = height / 2 - self.paddle_B.height / 2
        self.ball_pos = {"x": width / 2, "y": height / 2}

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

                if message["type"] == "input":
                    # move_up = message["data"]["move_up"]
                    # move_down = message["data"]["move_down"]
                    # space = message["data"]["space"]
                    keys = message["data"]["keys"]
                    # Traiter le message (par exemple, mettre à jour l'état du jeu)
                    if client_socket.getpeername() == self.clients[0].getpeername():
                        self.paddle_A.handle_keys(keys)
                    elif client_socket.getpeername() == self.clients[1].getpeername():
                        self.paddle_B.handle_keys(keys)

                    self.paddle_A_y = max(0, min(self.paddle_A.rect_paddle.y, height - self.paddle_A.height))
                    self.paddle_B_y = max(0, min(self.paddle_B.rect_paddle.y, height - self.paddle_B.height))

                    self.game.handle_events(keys=keys)

                    # Draw midline, score, check collision etc
                    self.game.draw_midline(color_midline)
                    self.game.draw_score(color_score)
                    self.paddle_A.draw()
                    self.paddle_B.draw()
                    self.ball.draw()
                    self.ball.draw_ball_move()
                    self.ball.check_collision()
                    self.game.scoring()

                # Envoyer la mise à jour à tous les clients
                update_message = {"type": "update", "data": {"paddle_A_y": self.paddle_A_y, "paddle_B_y": self.paddle_B_y, "ball_pos": self.ball_pos, "game_started": self.game.game_started}}
                for client in self.clients:
                    client.send(pickle.dumps(update_message))
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            self.clients.remove(client_socket)
            client_socket.close()


if __name__ == '__main__':
    server = PongServer("127.0.0.1", 5555)

    try:
        server.start()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.server_socket.close()
