import pygame
import random
import math
import multiprocessing
import time
import pygetwindow as gw
import pyautogui

pygame.init()
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
class Paddle:
    def __init__(self, x, ai=False):
        self.x = x
        self.y = HEIGHT // 2
        self.width = 10
        self.height = 100
        self.speed = 7
        self.ai = ai

    def move(self, ball=None):
        if self.ai:
            self.y = ball.y
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.y -= self.speed
            if keys[pygame.K_s]:
                self.y += self.speed
        self.y = max(0, min(self.y, HEIGHT - self.height))

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))
    def collides_with(self, ball):
        return (self.x < ball.x < self.x + self.width and self.y < ball.y < self.y + self.height)
player_paddle = Paddle(30)
ai_paddle = Paddle(WIDTH - 40, ai=True)

def ball_window(shared_ball):
    screen = pygame.display.set_mode((32, 32), pygame.NOFRAME)
    pygame.display.set_caption("Ball Window")
    pygame.display.flip()
    time.sleep(0.5)
    screen_width, screen_height = pyautogui.size()
    window = gw.getWindowsWithTitle("Ball Window")[0]

    radius = 8
    speed = 5
    angle = random.uniform(-math.pi / 4, math.pi / 4)
    dx = speed * random.choice([-1, 1])
    dy = speed * math.sin(angle)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        shared_ball.x += shared_ball.dx
        shared_ball.y += shared_ball.dy
        if shared_ball.y <= 0 or shared_ball.y >= HEIGHT:
            shared_ball.dy *= -1
        if shared_ball.x <= 0 or shared_ball.x >= WIDTH:
            shared_ball.dx *= -1
        screen.fill((0, 0, 0))
        pygame.draw.circle(screen, WHITE, (16, 16), radius)
        win_x = (screen_width - WIDTH) // 2 + int(shared_ball.x) - 16
        win_y = (screen_height - HEIGHT) // 2 + int(shared_ball.y) - 16
        window.moveTo(win_x, win_y)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
def paddle_window(shared_ball):
    paddle_screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Paddle")
    clock = pygame.time.Clock()
    player = Paddle(30)
    ai = Paddle(WIDTH - 40, ai=True)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        class FakeBall:
            def __init__(self, x, y):
                self.x = x
                self.y = y
        fake_ball = FakeBall(shared_ball.x, shared_ball.y)
        player.move(fake_ball)
        ai.move(fake_ball)
        if player.collides_with(fake_ball) and shared_ball.dx < 0:
            shared_ball.dx *= -1
        if ai.collides_with(fake_ball) and shared_ball.dx > 0:
            shared_ball.dx *= -1
        paddle_screen.fill((0, 0, 0))
        player.draw(paddle_screen)
        ai.draw(paddle_screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    manager = multiprocessing.Manager()
    shared_ball = manager.Namespace()
    shared_ball.x = WIDTH // 2
    shared_ball.y = HEIGHT // 2
    shared_ball.dx = random.choice([-5, 5])
    shared_ball.dy = random.uniform(-3, 3)
    ball_proc = multiprocessing.Process(target=ball_window, args=(shared_ball,))
    paddle_proc = multiprocessing.Process(target=paddle_window, args=(shared_ball,))

    paddle_proc.start()
    ball_proc.start()
    paddle_proc.join()
    ball_proc.join()
