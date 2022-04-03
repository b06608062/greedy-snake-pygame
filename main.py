import pygame
from pygame.locals import *
import sys
import random

FONT_STYLE = 'comicsansms'
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_RED = (180, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
GRAY = (128, 128, 128, 0.2)
SOUNDS = ['get_coin.wav', 'boom.wav', 'dead.wav']


class Snake(object):
    def __init__(self, widow_width, window_height, screen):
        self.head = [100, 100]
        self.body = []
        self.widow_width = widow_width
        self.window_height = window_height
        self.screen = screen

    def move(self, direction):
        if direction == "UP":
            self.head[1] = (self.head[1] - 20) % self.window_height
        elif direction == "DOWN":
            self.head[1] = (self.head[1] + 20) % self.window_height
        elif direction == "LEFT":
            self.head[0] = (self.head[0] - 20) % self.widow_width
        else:  # RIGHT
            self.head[0] = (self.head[0] + 20) % self.widow_width
        self.body.insert(0, list(self.head))

    def draw(self):
        for i in self.body:
            pygame.draw.rect(self.screen, BLUE, Rect(i[0], i[1], 20, 20))


class SnakeGame(object):
    def __init__(self, widow_width, window_height):
        self.widow_width = widow_width
        self.window_height = window_height
        pygame.init()
        pygame.display.set_caption('Greedy Snake@Jim')
        self.screen = pygame.display.set_mode((self.widow_width, self.window_height))
        self.snake = Snake(self.widow_width, self.window_height, self.screen)
        self.direction = "RIGHT"  # default direction
        self.clock = pygame.time.Clock()
        self.is_pause = False
        self.is_dead = False
        self.coin_position = [300, 300]
        self.coin = [pygame.image.load(f'./img/coin_{i}.jpg') for i in range(4)]
        self.boom_positions = [[200, 200]]
        self.boom = pygame.image.load('./img/TNT.jpg')
        self.mine_positions = [[400, 400]]
        self.mine = pygame.image.load('./img/mine.jpg')
        self.count = 0
        pygame.mixer.init()
        self.sounds = [pygame.mixer.Sound(f'./sound/{s}') for s in SOUNDS]
        for s in self.sounds:
            s.set_volume(0.2)
        pygame.mixer.music.load('./sound/bg.mp3')
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.direction != "DOWN":
                        self.direction = "UP"
                    elif event.key == pygame.K_DOWN and self.direction != "UP":
                        self.direction = "DOWN"
                    elif event.key == pygame.K_LEFT and self.direction != "RIGHT":
                        self.direction = "LEFT"
                    elif event.key == pygame.K_RIGHT and self.direction != "LEFT":
                        self.direction = "RIGHT"
                    elif event.key == pygame.K_SPACE:
                        self.paused()

            self.screen.fill(WHITE)

            # coin
            self.screen.blit(self.coin[self.count % 4], tuple(self.coin_position))
            self.count += 1

            # boom
            for i in self.boom_positions:
                self.screen.blit(self.boom, tuple(i))

            # mine
            for i in self.mine_positions:
                self.screen.blit(self.mine, tuple(i))

            # snake
            self.snake.move(self.direction)
            self.snake.draw()

            # score
            score_surf = pygame.font.SysFont(FONT_STYLE, 40).render(f"Score: {len(self.snake.body) - 1}", True, GRAY)
            self.screen.blit(score_surf, (20, 420))

            # get coin
            if self.snake.head == self.coin_position:
                self.sounds[0].play()
                self.boom_positions.append(self.gen_position())
                if len(self.mine_positions) <= 10:
                    self.mine_positions.append(self.gen_position())
                self.coin_position = self.gen_position()
            else:
                self.snake.body.pop()

            # hit boom
            if self.snake.head in self.boom_positions:
                self.sounds[1].play()
                self.boom_positions.remove(self.snake.head)
                if self.snake.body:
                    self.snake.body.pop()
                else:
                    self.game_over()

            # hit mine
            if self.snake.head in self.mine_positions:
                self.game_over()

            # hit body
            if self.snake.head in self.snake.body[1:]:
                self.game_over()

            pygame.display.update()
            self.clock.tick(10)

    def draw_button(self, text, x, y, w, h, c, ac):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        if x < mouse_pos[0] < x + w and y < mouse_pos[1] < y + h:
            pygame.draw.rect(self.screen, c[1], (x, y, w, h))
            if mouse_click == 1:
                ac()
        else:
            pygame.draw.rect(self.screen, c[0], (x, y, w, h))

        text_surf = pygame.font.SysFont(FONT_STYLE, 20).render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=(x + w / 2, y + h / 2))
        self.screen.blit(text_surf, text_rect)

    def game_start(self):
        self.screen.fill(WHITE)
        name_surf = pygame.font.SysFont(FONT_STYLE, 80).render('Greedy Snake', True, BLACK)
        name_rect = name_surf.get_rect(center=(self.widow_width / 2, self.window_height / 3))
        self.screen.blit(name_surf, name_rect)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()
            self.draw_button("GO", 110, 300, 100, 50, (DARK_GREEN, GREEN), self.run)
            self.draw_button("Exit", 430, 300, 100, 50, (DARK_RED, RED), self.exit)
            pygame.display.update()

    def paused(self):
        self.is_pause = True
        pygame.mixer.music.set_volume(0)
        pause_surf = pygame.font.SysFont(FONT_STYLE, 120).render("Paused", True, BLACK)
        pause_rect = pause_surf.get_rect(center=(self.widow_width / 2, self.window_height / 2))
        self.screen.blit(pause_surf, pause_rect)
        while self.is_pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.is_pause = False
                        pygame.mixer.music.set_volume(0.2)
            pygame.display.update()

    def gen_position(self):
        x = random.randint(0, self.widow_width / 20 - 1) * 20
        y = random.randint(0, self.window_height / 20 - 1) * 20
        if [x, y] in self.snake.body + self.boom_positions + self.mine_positions:
            return self.gen_position()
        else:
            return [x, y]

    def game_over(self):
        self.sounds[2].play()
        self.is_dead = True
        pygame.mixer.music.set_volume(0)
        game_over_surf = pygame.font.SysFont(None, 80).render("YOU DEAD!", False, RED)
        self.screen.blit(game_over_surf, ((self.widow_width - game_over_surf.get_width()) / 2,
                                          (self.window_height - game_over_surf.get_height()) / 3))
        while self.is_dead:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.is_dead = False
                        pygame.mixer.music.set_volume(0.2)
                        self.snake = Snake(self.widow_width, self.window_height, self.screen)
                        self.direction = "RIGHT"
                        self.coin_position = [300, 300]
                        self.boom_positions = [[200, 200]]
                        self.mine_positions = [[400, 400]]
                        self.count = 0

            pygame.display.update()

    @staticmethod
    def exit():
        pygame.quit()
        sys.exit()


def main():
    game = SnakeGame(640, 480)
    game.game_start()


if __name__ == "__main__":
    main()
