import socket
import threading

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
        self.ball_x = width / 2
        self.ball_y = height / 2
        self.pos_y = top_A
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

        # Set up pygame
        self.paddle_player = Paddle(color=color_paddle, left=left_A, top=top_A, move_up=pygame.K_UP,
                                    move_down=pygame.K_DOWN)
        self.paddle_next_player = Paddle(color=color_paddle, left=left_B, top=top_B, move_up=pygame.K_UP,
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
            self.paddle_next_player.rect_paddle.y = float(self.client_socket.recv(1024).decode("utf-8"))

    def create_thread(self, target):
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()

    def run_game(self):

        self.create_thread(self.accept_connections)

        pygame.display.set_caption("Pong HEY !!!")

        while self.run:
            self.screen.fill(color_screan)
            self.clock.tick(tick)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False

            keys = pygame.key.get_pressed()
            self.game.handle_events(keys)
            self.screen.fill("black")

            send_data = f"{self.paddle_player.rect_paddle.y},{self.ball.pos.x},{self.ball.pos.y},{self.game.game_started}"
            print(self.game.game_started)
            if self.client_socket:
                self.client_socket.send(send_data.encode('utf-8'))

            if self.game.game_started:
                # ON DRAW
                self.game.draw_midline(color_midline)
                self.game.draw_score(color_score)
                self.paddle_player.draw()
                self.paddle_next_player.draw()
                self.ball.draw()

                self.ball.draw_ball_move()
                self.paddle_player.handle_keys(keys)

                self.ball.check_collision(self.paddle_player, self.paddle_next_player)
                self.game.scoring()

                pygame.display.update()
            else:
                self.game.draw_start(color_start)
                pygame.display.flip()

        pygame.quit()


if __name__ == '__main__':
    pygame.init()

    server = PongServer()
    server.run_game()
