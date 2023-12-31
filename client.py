import threading
import pygame
import socket
from utils import *
from game import Ponggame, Paddle, Ball


class PongClient:
    def __init__(self):
        # Init Network
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = host_server
        self.port = port_server
        self.addr = (self.server, self.port)
        self.player = 2

        # Set up
        self.paddle_B = Paddle(color=color_paddle, left=left_B, top=top_B, move_up=pygame.K_UP, move_down=pygame.K_DOWN)
        self.paddle_A = Paddle(color=color_paddle, left=left_A, top=top_A, move_up=pygame.K_UP, move_down=pygame.K_DOWN)
        self.ball = Ball(color=color_ball, rad=rad, speed=speed)
        self.game = Ponggame(round_point, self.ball)

        # DATA
        self.started = False
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.run = True

    @staticmethod
    def create_thread(target):
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()

    def receive_data(self):
        while True:
            try:
                data = self.client_socket.recv(128).decode("utf-8")
                data = data.split(',')
                self.started = bool(data[3])
                self.paddle_A.rect_paddle.y = float(data[0])
                self.ball.pos.x = float(data[1])
                self.ball.pos.y = float(data[2])
                self.game.score_A = int(data[4])
                self.game.score_B = int(data[5])
            except Exception as e:
                print(f"Error : {e}")

    def run_game(self):
        self.client_socket.connect(self.addr)
        print("Connected to server")
        self.create_thread(self.receive_data)

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
            self.screen.fill("black")
            if self.started:
                # ON DRAW
                self.game.draw_midline(color_midline)
                self.game.draw_score(color_score)
                self.paddle_B.draw()
                self.paddle_A.draw()
                self.ball.draw()

                self.paddle_B.handle_keys(keys)
                self.client_socket.send(str(self.paddle_B.rect_paddle.y).encode('utf-8'))

                self.ball.check_collision(self.paddle_A, self.paddle_B)
                self.game.scoring(increment=0)

            else:
                self.game.draw_start(color_start, self.player)   # DIRE QUE JOUEUR 2 ATTENDRE JOUEUR 1

            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    client = PongClient()
    client.run_game()
