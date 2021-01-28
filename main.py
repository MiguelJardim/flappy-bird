'''
Flappy Bird: remake of the original game Flappy Bird.
@author Miguel Gonçalves Jardim
'''

import pygame
from pygame import mixer
import time
import random
import math


class Bird():
    def __init__(self, position, image):
        self.x, self.y = position
        self.inicial_y = self.y
        self.velocity = 0
        self.image = image
        self.available = 1

        self.width = 36
        self.height = 26

        self.angle = 0

        self.falling = 100

    def draw(self, screen):
        screen.blit(pygame.transform.rotate(self.image, self.angle),
                    (self.x - self.width/2, self.y - self.height/2))

    def update_position(self, start, now):
        self.y = self.inicial_y + self.velocity * \
            (now-start) + 0.5 * 1500 * (now-start)**2

        self.hit_ceiling(start, now)

        if self.falling < 0:
            self.angle -= 0.5 * (now-start)
            if self.angle < - 90:
                self.angle = - 90
        else:
            self.falling -= now - start

    def jump(self):
        self.velocity = -400
        self.inicial_y = self.y

        self.angle = 20

        self.falling = 100

    def hit_floor(self):
        if self.y + 13 >= 384:
            return True

    def hit_ceiling(self, start, now):
        if self.y < 13:
            self.y = 13
            self.inicial_y = self.y
            self.velocity = self.velocity * (now - start)
            return True
        return False

    def hit_tube(self, tubes, opening_size):
        for tube in tubes:
            if self.x + 18 >= tube[0] - 26 and self.x - 18 <= tube[0] + 26 \
                    and (self.y - 13 <= tube[1] - opening_size/2
                         or self.y + 13 >= tube[1] + opening_size/2):
                return True
        return False

    def point(self, tubes):
        pointed = False
        for tube in tubes:
            if tube[0] - 26 < self.x < tube[0] + 26 and self.x >= tube[0] \
                    and self.available == 1:
                self.available = 0
                return True
            elif tube[0] - 26 < self.x < tube[0] + 26 and self.x >= tube[0]:
                pointed = True
        if not pointed:
            self.available = 1
        return False

    def fall(self, game):
        self.velocity = 0
        self.inicial_y = self.y
        start = time.time()

        while not self.hit_floor():

            now = time.time()

            self.angle -= 0.3 * (now-start)
            if self.angle < - 90:
                self.angle = - 90

            self.y = self.inicial_y + self.velocity * \
                (now-start) + 0.5 * 1500 * (now-start)**2

            game.screen.fill((0, 0, 0))

            game.set_sky()
            game.set_tubes()
            game.set_ground()

            self.draw(game.screen)

            pygame.display.update()

    def hover(self, delta):
        now = time.time()
        self.y = self.inicial_y + 7 * math.cos(5 * now)


class Game():

    def __init__(self, size, bird):

        # title and icon
        pygame.display.set_caption("Flappy Bird")
        pygame.display.set_icon(pygame.image.load("img/bird.png"))

        self.score = 0

        # create the screen
        self.width, self.height = size
        self.size = size
        self.screen = pygame.display.set_mode((self.width, self.height))

        # background
        self.sky = pygame.image.load("img/bg.png")
        self.ground = pygame.image.load("img/ground.png")

        self.up_tube = pygame.image.load("img/up_tube.png")
        self.down_tube = pygame.image.load("img/down_tube.png")

        self.bird = bird

        self.last_update = time.time()
        self.last_position = 0

        self.tubes = [(2*self.width, random.randint(100, 284))]

        self.opening_size = 100

    def set_sky(self):
        self.screen.blit(self.sky, (0, 0))

    def set_ground(self):
        self.screen.blit(self.ground, (0, 384))
        self.last_update = time.time()

    def set_tubes(self):
        for tube in self.tubes:
            self.screen.blit(
                self.up_tube, (tube[0] - 26, tube[1] - 320 -
                               self.opening_size/2))
            self.screen.blit(
                self.down_tube, (tube[0] - 26, tube[1] + self.opening_size/2))

    def move_scene(self, move_tubes=True):
        delta = time.time() - self.last_update
        self.last_update = time.time()
        x = 150 * delta
        self.screen.fill((0, 0, 0))
        self.set_sky()

        if move_tubes:
            max_x = self.tubes[0][0]
            tubes = []
            for i in range(len(self.tubes)):
                if self.tubes[i][0] > max_x:
                    max_x = self.tubes[i][0]
                if self.tubes[i][0] - x > -100:
                    tubes.append((self.tubes[i][0] - x, self.tubes[i][1]))

            # add tube
            if max_x < self.width - 170:
                tubes.append((self.width + 26, random.randint(100, 284)))

            self.tubes = tubes

            self.set_tubes()

        if self.last_position <= -self.width:
            self.last_position = 0

        self.last_position -= x

        self.screen.blit(self.ground, (self.last_position, 384))
        self.screen.blit(self.ground, (self.last_position + self.width, 384))

    def game_over(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        main()

    def start_screen(self):
        running = True
        start = time.time()
        while running:
            now = time.time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        start = time.time()
                        self.bird.jump()

                        sound = mixer.Sound("sound/wing.wav")
                        sound.play()

                        running = False

            self.move_scene(move_tubes=False)

            self.bird.hover(now - start)
            self.bird.draw(self.screen)

            pygame.display.update()

        return True

    def run(self):
        # initialize the pygame
        pygame.init()

        sound = mixer.Sound("sound/swooshing.wav")
        sound.play()

        if not self.start_screen():
            return

        # game loop
        running = True
        start = time.time()
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        start = time.time()
                        self.bird.jump()

                        sound = mixer.Sound("sound/wing.wav")
                        sound.play()

            now = time.time()
            self.bird.update_position(start, now)

            if self.bird.hit_floor():
                sound = mixer.Sound("sound/hit.wav")
                sound.play()
                sound = mixer.Sound("sound/die.wav")
                sound.play()
                self.game_over()
                return
            if self.bird.point(self.tubes):
                sound = mixer.Sound("sound/point.wav")
                sound.play()
                self.score += 1
            if self.bird.hit_tube(self.tubes, self.opening_size):
                sound = mixer.Sound("sound/hit.wav")
                sound.play()
                sound = mixer.Sound("sound/die.wav")
                sound.play()
                self.bird.fall(self)
                self.game_over()
                return

            self.move_scene()

            self.bird.draw(self.screen)

            self.display_score()

            pygame.display.update()

    def display_score(self):
        font = pygame.font.Font('font/numbers.ttf', 64)
        score_text = font.render(str(self.score), True, (255, 255, 255))

        score_position = score_text.get_rect(
            center=(self.width/2, self.height/5))

        self.screen.blit(score_text, score_position)


def main():
    width, heigth = 288, 480
    image = pygame.image.load("img/bird.png")
    bird = Bird((width / 3, heigth / 2), image)
    game = Game((width, heigth), bird)

    game.run()


if __name__ == '__main__':
    main()
