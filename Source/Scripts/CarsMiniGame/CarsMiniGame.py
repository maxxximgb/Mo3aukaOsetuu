import random
import pygame
import cv2
import time

from Globals.SharedFunctions import switch

rules, game_state = [None] * 2

class CarsMiniGame:
    def __init__(self):
        self.level = None
        self.Bus = Bus
        self.video = None
        self.screen = pygame.Surface
        self.collidesong = None
        self.clock = pygame.time.Clock
        self.score = int
        self.moving_cars = pygame.sprite.Group
        self.parked_cars = pygame.sprite.Group
        self.start_time = time.time
        self.game_over = bool
        self.blink_timer = 0
        self.show_hitboxes = bool
        self.debug_message_timer = int
        self.loaded = False

    def exec(self):
        global rules, game_state
        from Globals.Variables import rules, game_state
        if not self.loaded:
            self.video = cv2.VideoCapture('../Media/RoadVid.mp4')
            self.collidesong = pygame.mixer.Sound('../Media/collide.mp3')
            self.clock = pygame.time.Clock()
            self.moving_cars = pygame.sprite.Group()
            self.parked_cars = pygame.sprite.Group()
            self.blink_timer = 0
            self.show_hitboxes = False
            self.debug_message_timer = 0
            self.loaded = True
        self.start_time = time.time()
        self.screen = pygame.display.set_mode((int(self.video.get(3)), int(self.video.get(4))))
        self.Bus = Bus('../Media/Bus.png')
        pygame.display.set_caption('Переход в уровень')
        self.game_over = False
        self.score = 10
        self.create_cars()
        self.level = game_state.currentlvl

        rules.append(self.render)

    def create_cars(self):
        positions = [self.screen.get_height() // 4 + 100, self.screen.get_height() // 2 + 100, (self.screen.get_height() * 3) // 4 + 100]
        images = ['../Media/GreenCar.png', '../Media/RedCar.png', '../Media/YellowCar.png']
        pos1, pos2 = random.sample(positions, 2)
        img1, img2 = random.sample(images, 2)
        self.moving_cars.add(MovingCar(img1, self.screen.get_width() + 500, pos1, random.randint(10, 20)),
                             MovingCar(img2, self.screen.get_width() + 500, pos2, random.randint(10, 20)))
        self.parked_cars.add(ParkedCar('../Media/BlueCar.png', self.screen.get_width() + random.randint(100, 300), 70),
                             ParkedCar('../Media/SportCar.png', self.screen.get_width() + random.randint(900, 1200), 70))

    def reset_game(self):
        self.score = 10
        self.start_time = time.time()
        self.game_over = False
        self.moving_cars.empty()
        self.parked_cars.empty()
        self.create_cars()
        self.Bus.rect.center = (170, 300)

    def render(self):
        ret, frame = self.video.read()
        if not ret:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        self.screen.blit(frame, (0, 0))

        self.Bus.update()
        self.moving_cars.update()
        self.parked_cars.update()
        self.moving_cars.draw(self.screen)
        self.parked_cars.draw(self.screen)

        if pygame.sprite.spritecollideany(self.Bus, self.moving_cars) or pygame.sprite.spritecollideany(self.Bus, self.parked_cars):
            if self.blink_timer == 0:
                self.score -= 1
                self.collidesong.play()
                self.blink_timer = time.time()
                if self.score <= 0:
                    self.reset_game()

        if self.blink_timer > 0 and time.time() - self.blink_timer < 2:
            if int((time.time() - self.blink_timer) * 5) % 2 == 0:
                self.screen.blit(self.Bus.image, self.Bus.rect)
        else:
            self.blink_timer = 0
            self.screen.blit(self.Bus.image, self.Bus.rect)

        if self.show_hitboxes:
            for sprite in [self.Bus] + list(self.moving_cars) + list(self.parked_cars):
                pygame.draw.rect(self.screen, (255, 0, 0), sprite.rect, 2)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_F9] and self.debug_message_timer == 0:
            self.show_hitboxes = not self.show_hitboxes
            self.debug_message_timer = time.time()

        if self.debug_message_timer > 0 and time.time() - self.debug_message_timer < 2:
            font = pygame.font.Font(None, 36)
            message = "Отладка: Включены хитбоксы" if self.show_hitboxes else "Отладка: Выключены хитбоксы"
            self.screen.blit(font.render(message, True, (255, 255, 255)), (10, self.screen.get_height() - 50))
        else:
            self.debug_message_timer = 0

        elapsed_time = time.time() - self.start_time
        remaining_time = max(0, 30 - int(elapsed_time))
        font = pygame.font.Font(None, 36)
        text = f"Счет: {self.score}, До приезда: {remaining_time} секунд" if remaining_time > 0 else f"Счет: {self.score}, Закончите обьезжать машины"
        self.screen.blit(font.render(text, True, (0, 0, 0)), (self.screen.get_width() - 400, 10) if remaining_time > 0 else (self.screen.get_width() - 500, 10))

        if remaining_time <= 0:
            self.game_over = True

        self.clock.tick(30)
        if self.game_over:
            if self.Bus.rect.x > self.screen.get_width():
                self.Unload()
                game_state.score += self.score
                switch(self, game_state.gameclasses.CityScreen, self.screen, render_needed=False)
            if not self.moving_cars and not self.parked_cars:
                self.Bus.rect.x += 20

        if not self.moving_cars and not self.game_over:
            self.create_cars()

    def Unload(self):
        if self.render in rules: rules.remove(self.render)

class Bus(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect(center=(170, 300))

    def update(self):
        keys = pygame.key.get_pressed()
        self.rect.y += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * 13
        self.rect.y = max(140, min(self.rect.y, 720 - self.rect.height))

class ParkedCar(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x -= 12
        if self.rect.right < 0:
            self.kill()

class MovingCar(pygame.sprite.Sprite):
    def __init__(self, image, x, y, speed):
        super().__init__()
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()