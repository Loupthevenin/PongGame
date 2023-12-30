from utils import *
from game import Ponggame, Paddle, Ball
from network import Network


class PongClient:
    def __init__(self):
        self.net = Network(server=host_server, port=port_server)

        # Init Pygame
        self.screan = pygame.display.set_mode((width, height))

        # Set up
        self.game = Ponggame(round_point)
        self.paddle_A = Paddle(color=color_paddle, left=left_A, top=top_A, move_up=pygame.K_UP, move_down=pygame.K_DOWN)
        self.paddle_B = Paddle(color=color_paddle, left=left_B, top=top_B, move_up=pygame.K_UP, move_down=pygame.K_DOWN)
        self.ball = Ball(color=color_ball, rad=rad, speed=speed)

    def send_data(self, type):
        if type == "paddle":
            data = str(self.net.id) + ":" + str(self.paddle_A.rect_paddle.x) + "," + str(self.paddle_A.rect_paddle.y)
            reply = self.net.send(data)
            return reply
        elif type == "ball":
            data = str(self.net.id) + ":" + str(self.ball.pos.x) + "," + str(self.ball.pos.y)
            reply = self.net.send(data)
            return reply

    @staticmethod
    def parse_data(data):
        try:
            d = data.split(":")[1].split(",")
            return int(d[0]), int(d[1])
        except:
            return 0, 0

    def run_game(self):
        pygame.init()
        pygame.display.set_caption("Pong HEY !!!")
        clock = pygame.time.Clock()
        run = True

        while run:
            self.screan.fill(color_screan)
            clock.tick(tick)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            keys = pygame.key.get_pressed()

            self.game.draw_midline(color_midline)
            self.game.draw_score(color_score)
            self.paddle_A.draw()
            self.paddle_B.draw()
            self.ball.draw()

            # SEND POS PADDLE ET POS BALL
            # ATTENTION INVERSER POUR LE CLIENT B
            self.paddle_B.rect_paddle.x, self.paddle_B.rect_paddle.y = self.parse_data(self.send_data("paddle"))
            # self.ball.pos.x, self.ball.pos.y = self.parse_data(self.send_data("ball"))

            self.paddle_A.handle_keys(keys)
            self.ball.draw_ball_move()
            if self.ball.check_collision():
                self.ball.pos = pygame.Vector2(self.ball.x, self.ball.y)

            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    client = PongClient()
    client.run_game()
