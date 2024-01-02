import pygame
import random


class Ponggame:
    def __init__(self, score_max, ball):
        self.score_A = 0
        self.score_B = 0
        self.game_started = False
        self.score_max = score_max
        self.ball = ball

    @staticmethod
    def draw_midline(line_color):
        line_width = 80
        line_color = line_color
        line_spacing = 100

        for y in range(0, height, line_spacing):
            pygame.draw.line(screan, line_color, (width / 2, y), (width / 2, y + line_width), 20)

    def draw_score(self, font_color):
        font_size = 200
        font_color = font_color
        font = pygame.font.Font(None, font_size)

        score_A_text = f"{self.score_A}"
        text_A_surface = font.render(score_A_text, True, font_color)
        text_A_rect = text_A_surface.get_rect(center=(width / 4, 100))

        score_B_text = f"{self.score_B}"
        text_B_surface = font.render(score_B_text, True, font_color)
        text_B_rect = text_B_surface.get_rect(center=((width / 2) + (width / 4), 100))

        screan.blit(text_A_surface, text_A_rect)
        screan.blit(text_B_surface, text_B_rect)

    @staticmethod
    def draw_start(font_color):
        font_size = 50
        font_color = font_color
        font = pygame.font.Font(None, font_size)

        text_surface = font.render("Appuyez sur ESPACE pour commencer", True, font_color)
        text_rect = text_surface.get_rect(center=(width / 2, height / 2))

        screan.blit(text_surface, text_rect)

    def scoring(self):
        if not self.check_scoring():
            if ball_instance.check_points() == "A LOSE":
                self.score_B += 1
                self.ball.reset_ball()
            elif ball_instance.check_points() == "B LOSE":
                self.score_A += 1
                self.ball.reset_ball()
        elif self.check_scoring():
            # YOU WIN
            # YOU LOSE
            self.score_A = 0
            self.score_B = 0
            self.ball.reset_ball()

    def check_scoring(self):
        if self.score_A >= self.score_max:
            return True
        if self.score_B >= self.score_max:
            return True
        return False

    def reset_run(self):
        pass

    def handle_events(self, keys):
        if keys[pygame.K_SPACE]:
            self.game_started = True


class Paddle:
    def __init__(self, color, left, top, move_up, move_down):
        self.width = 10
        self.height = 100
        self.color = color
        self.left = left
        self.top = top
        # Create rect
        self.rect_paddle = pygame.Rect((self.left, self.top, self.width, self.height))
        # Distance parcourut
        self.dist = 15
        self.move_up = move_up
        self.move_down = move_down

    def draw_rect_mov(self, x, y):
        self.rect_paddle = self.rect_paddle.move(x * self.dist, y * self.dist)
        self.draw()
        # pygame.display.update()

    def draw(self):
        pygame.draw.rect(screan, self.color, self.rect_paddle)

    def handle_keys(self, keys):
        if self.test_border() not in [0, 1]:
            if keys[self.move_up]:
                self.draw_rect_mov(0, -1)
            if keys[self.move_down]:
                self.draw_rect_mov(0, 1)
        else:
            if self.test_border() == 0:
                if keys[self.move_down]:
                    self.draw_rect_mov(0, 1)
            elif self.test_border() == 1:
                if keys[self.move_up]:
                    self.draw_rect_mov(0, -1)

    def test_border(self) -> int:
        rect_Y_top = self.rect_paddle.y
        rect_Y_bot = self.rect_paddle.y + self.height
        if rect_Y_top <= 0:
            return 0
        elif rect_Y_bot >= height:
            return 1
        return 2


class Ball:
    def __init__(self, color, rad, speed):
        self.x = width / 2
        self.y = height / 2
        self.rad = rad
        self.color = color
        self.speed = speed
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.pos = pygame.Vector2(self.x, self.y)

    def draw(self):
        pygame.draw.circle(screan, self.color, self.pos, self.rad)

    def move(self):
        self.pos += self.direction * self.speed

    def draw_ball_move(self):
        self.move()
        self.draw()
        pygame.display.flip()

    def check_collision(self, paddle_A, paddle_B):
        max_Y = height
        min_Y = 0
        ball_rect = pygame.Rect(self.pos.x - self.rad, self.pos.y - self.rad, 2 * self.rad, 2 * self.rad)
        self.paddle_A = paddle_A
        self.paddle_B = paddle_B

        # Collision : mur Haut
        if self.pos.y + self.rad > max_Y or self.pos.y - self.rad < min_Y:
            self.direction.y *= -1

        # Collision Paddle
        if self.paddle_A.rect_paddle.colliderect(ball_rect) or self.paddle_B.rect_paddle.colliderect(ball_rect):
            self.direction.x *= -1

    def check_points(self) -> str:
        max_X = width
        min_X = 0

        # Le joueur B a perdu.
        if self.pos.x + self.rad > max_X:
            return "B LOSE"
        # Le joueur A a perdu
        elif self.pos.x - self.rad < min_X:
            return "A LOSE"

    def reset_ball(self):
        self.pos = pygame.Vector2(self.x, self.y)
        pygame.time.wait(300)


pygame.init()


width = 1200
height = 700
screan = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()


# Set up

paddle_A = Paddle((240, 255, 255), 20, 300, pygame.K_z, pygame.K_s)
paddle_B = Paddle((240, 255, 255), 1170, 300, pygame.K_UP, pygame.K_DOWN)
ball_instance = Ball((240, 250, 250), 10, 15)
game = Ponggame(5, ball_instance)

run = True


if __name__ == '__main__':
    # main Loop
    while run:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # PRESS SPACE
        key = pygame.key.get_pressed()
        game.handle_events(keys=key)
        screan.fill("black")

        # Game Start
        if game.game_started:
            # La partie DRAW
            game.draw_midline((240, 255, 255))
            game.draw_score((200, 250, 250))
            paddle_A.draw()
            paddle_B.draw()
            # La partie mouvements
            paddle_A.handle_keys(keys=key)
            paddle_B.handle_keys(keys=key)

            ball_instance.draw()
            ball_instance.draw_ball_move()
            ball_instance.check_collision(paddle_A, paddle_B)

            game.scoring()

            pygame.display.update()
        # Starting
        else:
            game.draw_start((240, 250, 250))
            pygame.display.flip()

    pygame.quit()
