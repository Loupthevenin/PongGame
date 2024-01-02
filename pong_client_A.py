import threading

from utils import *
from game import Ponggame, Paddle, Ball
from network import Network
import time


class PongClient:
    def __init__(self):
        # Init Network
        self.net = Network(server=host_server, port=port_server)
        self.player_id = self.net.id
        print(self.player_id)
        self.ready_to_start = threading.Event()

        # Verif ID
        if self.player_id not in [1, 2]:
            raise ValueError(f"Invalid player_id: {self.player_id}")

        self.screen = pygame.display.set_mode((width, height))

        # Set up
        if self.player_id == 1:
            self.paddle_player = Paddle(color=color_paddle, left=left_A, top=top_A, move_up=pygame.K_UP, move_down=pygame.K_DOWN)
            self.paddle_next_player = Paddle(color=color_paddle, left=left_B, top=top_B, move_up=pygame.K_UP, move_down=pygame.K_DOWN)
        elif self.player_id == 2:
            self.paddle_player = Paddle(color=color_paddle, left=left_B, top=top_B, move_up=pygame.K_UP, move_down=pygame.K_DOWN)
            self.paddle_next_player = Paddle(color=color_paddle, left=left_A, top=top_A, move_up=pygame.K_UP, move_down=pygame.K_DOWN)

        self.ball = Ball(color=color_ball, rad=rad, speed=speed)
        self.game = Ponggame(round_point, self.ball)

    def send_data(self, type):
        reply = {}
        if type == "paddle":
            data = {
                "player_id": self.player_id,
                "position": {"paddle_y": self.paddle_player.rect_paddle.y}
            }
            reply = self.net.send(data)
            return reply
        elif type == "ball":
            data = {
                "player_id": self.player_id,
                "ball": {"ball_pos_x": self.ball.pos.x, "ball_pos_y": self.ball.pos.y}
            }
            reply = self.net.send(data)
            return reply
        elif type == "space":
            data = {
                "player_id": self.player_id,
                "started": self.game.game_started
            }
            reply = self.net.send(data)
            return reply

    def parse_data(self, data):
        print(f"parse: {data}")
        if data:
            if "position" in data:
                try:
                    d = data["position"]["paddle_y"]
                    print(d)
                    return int(d)
                except:
                    return self.paddle_next_player.rect_paddle.y
            elif "ball" in data:
                try:
                    d = data["ball"]
                    return d["ball_pos_x"], d["ball_pos_y"]
                except:
                    return self.ball.pos.x, self.ball.pos.y
            elif "started" in data:
                try:
                    d = data["started"]
                    return bool(d)
                except:
                    return self.game.game_started
        else:
            return False

    def synchronize_client(self):
        print("Waiting for synchronization signal...")
        self.ready_to_start.wait()
        print("Synchronization signal received. Continuing with the game.")

    def run_game(self):
        pygame.init()

        pygame.display.set_caption("Pong HEY !!!")
        clock = pygame.time.Clock()
        run = True

        reply = False

        while run:
            self.screen.fill(color_screan)
            clock.tick(tick)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            keys = pygame.key.get_pressed()
            self.game.handle_events(keys)
            self.screen.fill("black")

            if reply or self.game.game_started:
                # ON DRAW
                self.game.draw_midline(color_midline)
                self.game.draw_score(color_score)
                self.paddle_player.draw()
                self.paddle_next_player.draw()
                self.ball.draw()

                # SEND POS PADDLE
                if self.player_id == 1:
                    received_value = self.parse_data(self.send_data("paddle"))
                    print(f"Type de la valeur reçue : {received_value}:{type(received_value)}")
                    self.paddle_next_player.rect_paddle.y = received_value
                elif self.player_id == 2:
                    received_value = self.parse_data(self.send_data("paddle"))
                    print(f"Type de la valeur reçue : {received_value}:{type(received_value)}")
                    self.paddle_next_player.rect_paddle.y = received_value

                self.paddle_player.handle_keys(keys)
                self.paddle_player.draw()
                self.paddle_next_player.draw()

                # SEND DIRECTION AND POS BALL
                if self.player_id == 1:
                    print("ici")
                    x, y = self.parse_data(self.send_data("ball"))
                    self.ball.pos.x, self.ball.pos.y = x, y
                    self.ball.draw_ball_move()
                elif self.player_id == 2:
                    print("ici2")
                    x, y = self.parse_data(self.send_data("ball"))
                    self.ball.pos.x, self.ball.pos.y = x, y
                    self.ball.draw_ball_move()

                time.sleep(0.3)
                self.ball.check_collision(self.paddle_player, self.paddle_next_player)
                self.game.scoring()

                pygame.display.update()

            else:
                self.game.draw_start(color_start)
                pygame.display.flip()

                # SEND SPACE
                reply = self.parse_data(self.send_data("space"))
                print(f"reply space : {reply}")
                print(f"game_started space : {self.game.game_started}")

        pygame.quit()


if __name__ == '__main__':
    client = PongClient()
    client.synchronize_client()
    print("on y es")
    client.run_game()
