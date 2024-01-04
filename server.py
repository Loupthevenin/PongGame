import socket
import threading
import pygame

from game import Ponggame, Paddle, Ball
from utils import *


class PongServer:
    def __init__(self):
        # Network
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = host_server
        self.port = port_server
        self.socket.bind((self.server, self.port))
        self.socket.listen(1)
        self.client_socket, self.addr = None, None
        self.player = 1

        # DATA
        self.run = True
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

        # Set up pygame
        self.paddle_A = Paddle(color=color_paddle, left=left_A, top=top_A, move_up=pygame.K_UP,
                               move_down=pygame.K_DOWN)
        self.paddle_B = Paddle(color=color_paddle, left=left_B, top=top_B, move_up=pygame.K_UP,
                               move_down=pygame.K_DOWN)
        self.ball = Ball(color=color_ball, rad=rad, speed=speed)
        self.game = Ponggame(round_point, self.ball)

    def accept_connections(self):
        while True:
            self.client_socket, self.addr = self.socket.accept()
            print(f"{self.client_socket}:{self.addr}")
            self.receive_data()

    def receive_data(self):
        while True:
            self.paddle_B.rect_paddle.y = float(self.client_socket.recv(1024).decode("utf-8"))

    @staticmethod
    def create_thread(target):
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()

    def run_game(self):

        self.create_thread(self.accept_connections)

        pygame.init()
        pygame.display.set_caption("Pong HEY !!!")

        while self.run:
            self.screen.fill(color_screan)
            self.clock.tick(tick)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.run = False

            keys = pygame.key.get_pressed()
            self.game.handle_events(keys)
            self.screen.fill("black")

            send_data = f"{self.paddle_A.rect_paddle.y},{self.ball.pos.x},{self.ball.pos.y},{self.game.game_started},{self.game.score_A},{self.game.score_B}"
            if self.client_socket:
                self.client_socket.send(send_data.encode('utf-8'))

            if self.game.game_started:
                # ON DRAW
                self.game.draw_midline(color_midline)
                self.game.draw_score(color_score)
                self.paddle_A.draw()
                self.paddle_B.draw()
                self.ball.draw()

                self.ball.draw_ball_move()
                self.ball.speed_up()
                self.paddle_A.handle_keys(keys)

                self.ball.check_collision(self.paddle_A, self.paddle_B)
                self.game.scoring()

            else:
                self.game.draw_start(color_start, self.player)

            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    server = PongServer()
    server.run_game()
