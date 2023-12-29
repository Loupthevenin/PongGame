import socket
import threading
import pickle
from utils import *
from game import Ponggame, Paddle, Ball


class PongClient:
    def __init__(self, host, port, player):
        self.host = host
        self.port = port
        self.player = player
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Init Pygame
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screan = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Pong HEY !!!")

        # Set up
        self.game = Ponggame(round_point)
        self.paddle_A = Paddle(color=color_paddle, left=left_A, top=top_A, move_up=pygame.K_z, move_down=pygame.K_s)
        self.paddle_B = Paddle(color=color_paddle, left=left_B, top=top_B, move_up=pygame.K_UP, move_down=pygame.K_DOWN)
        self.ball = Ball(color=color_ball, rad=rad, speed=speed)

        # server
        self.paddle_A_y = height / 2 - self.paddle_A.height / 2
        self.paddle_B_y = height / 2 - self.paddle_B.height / 2
        self.ball_pos = {"x": width / 2, "y": height / 2}

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

                if message["type"] == "update":
                    self.paddle_A_y = message["data"]["paddle_A_y"]
                    self.paddle_B_y = message["data"]["paddle_B_y"]
                    self.ball_pos = message["data"]["ball_pos"]
                # Traiter la mise à jour de l'état du jeu (par exemple, dessiner les raquettes et la balle)

        except Exception as e:
            print(f"Error receiving messages: {e}")
        finally:
            self.client_socket.close()

    def send_message(self, message):
        self.client_socket.send(pickle.dumps(message))

    def run_game(self):
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            keys = pygame.key.get_pressed()
            if self.player == "A":
                update_data = {"type": "input", "data": {"move_up": keys[pygame.K_w], "move_down": keys[pygame.K_s]}}
                self.send_message(update_data)
            elif self.player == "B":
                update_data = {"type": "input", "data": {"move_up": keys[pygame.K_UP], "move_down": keys[pygame.K_DOWN]}}
                self.send_message(update_data)

            self.screan.fill(color_screan)
            pygame.display.flip()
            self.clock.tick(tick)

            # Mets a jours les pos paddle et ball
            try:
                data = self.client_socket.recv(1024)
                if data:
                    update_data = pickle.loads(data)

                    self.paddle_A_y = update_data["data"]["paddle_A_y"]
                    self.paddle_B_y = update_data["data"]["paddle_B_y"]
                    self.ball_pos = update_data["data"]["ball_pos"]

                    # Draw
                    self.paddle_A.draw_rect_mov(0, self.paddle_A_y)
                    self.paddle_B.draw_rect_mov(0, self.paddle_B_y)
                    self.ball_pos = pygame.Vector2(self.ball_pos["x"], self.ball_pos["y"])
                    self.ball.draw()
            except Exception as e:
                print(f"Error receiving update from server: {e}")


if __name__ == '__main__':
    client = PongClient(host_server, port_server, player_B)
    client.connect()
    client.run_game()
