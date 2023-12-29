import socket
import threading
import pickle

import pygame

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

    def close_connection(self):
        if self.client_socket:
            self.client_socket.close()

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
        except Exception as e:
            print(f"Error receiving messages: {e}")
        finally:
            self.client_socket.close()

    def send_message(self, message):
        try:
            if self.client_socket.fileno() != -1:
                self.client_socket.send(pickle.dumps(message))
        except OSError as e:
            print(f"Erro sending message: {e}")

    def run_game(self):
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            keys = pygame.key.get_pressed()
            if self.player == "A":
                # update_data = {"type": "input", "data": {"move_up": keys[pygame.K_w], "move_down": keys[pygame.K_s], "space": keys[pygame.K_SPACE]}}
                update_data = {"type": "input", "data": {"keys": keys}}
                self.send_message(update_data)
            elif self.player == "B":
                # update_data = {"type": "input", "data": {"move_up": keys[pygame.K_UP], "move_down": keys[pygame.K_DOWN], "space": keys[pygame.K_SPACE]}}
                update_data = {"type": "input", "data": {"keys": keys}}
                self.send_message(update_data)

            self.screan.fill(color_screan)
            pygame.display.flip()
            self.clock.tick(tick)

            try:
                print("Waiting for data...")
                data = self.client_socket.recv(1024)
                print("Data received:", data)
                if data:
                    update_data = pickle.loads(data)

                    self.game.game_started = update_data.get("game_started", False)

                    # if update_data.get("game_started"):
                    if self.game.game_started:
                        self.game.draw_midline(color_midline)
                        self.game.draw_score(color_score)
                        self.paddle_A.draw_rect_mov(0, update_data["data"]["paddle_A_y"])
                        self.paddle_B.draw_rect_mov(0, update_data["data"]["paddle_B_y"])
                        self.ball_pos = pygame.Vector2(update_data["data"]["ball_pos"]["x"], update_data["data"]["ball_pos"]["y"])
                        self.ball.draw()
                        pygame.display.update()
                    else:
                        self.game.draw_start(color_start)
                        pygame.display.flip()

            except Exception as e:
                print(f"Error receiving update from server: {e}")


if __name__ == '__main__':
    client = PongClient("127.0.0.1", port_server, player_A)

    try:
        client.connect()
        client.run_game()
    except KeyboardInterrupt:
        print("Client shutting down...")
    finally:
        client.client_socket.close()
