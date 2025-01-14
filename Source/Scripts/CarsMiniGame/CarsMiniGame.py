import random
import pygame
from Globals.Globals import rules, events
import cv2
import time

class CarsMiniGame:
    def __init__(self):
        self.Bus = Bus('../Media/Bus.png')
        self.video = cv2.VideoCapture('../Media/RoadVid.mp4')
        self.screen = pygame.display.set_mode((int(self.video.get(3)), int(self.video.get(4))))
        pygame.display.set_caption('Переход в уровень')
        self.clock = pygame.time.Clock()
        self.score = 10
        rules.append(self.render)
        self.moving_cars = pygame.sprite.Group()
        self.parked_cars = pygame.sprite.Group()
        self.create_moving_cars()
        self.create_parked_cars()
        self.start_time = time.time()
        self.game_over = False

    def create_moving_cars(self):
        pos1, pos2 = random.sample(
            [self.screen.get_height() // 4 + 100, self.screen.get_height() // 2 + 100, (self.screen.get_height() * 3) // 4 + 100], 2)
        img1, img2 = random.sample(
            ['../Media/GreenCar.png', '../Media/RedCar.png', '../Media/YellowCar.png'], 2)
        self.moving_cars.add(
            MovingCar(img1, self.screen.get_width() + 500, pos1, random.randint(10, 20)),
            MovingCar(img2, self.screen.get_width() + 500, pos2, random.randint(10, 20))
        )

    def create_parked_cars(self):
        parked_car1 = ParkedCar('../Media/BlueCar.png', self.screen.get_width() + random.randint(100, 300), 70)
        parked_car2 = ParkedCar('../Media/SportCar.png', self.screen.get_width() + random.randint(900, 1500), 70)
        self.parked_cars.add(parked_car1, parked_car2)

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
        self.moving_cars.draw(self.screen)
        self.parked_cars.update()
        self.parked_cars.draw(self.screen)
        self.screen.blit(self.Bus.image, self.Bus.rect)
        elapsed_time = time.time() - self.start_time
        remaining_time = max(0, 30 - int(elapsed_time))
        font = pygame.font.Font(None, 36)
        text = font.render(f"Счет: {self.score}, До приезда: {remaining_time} секунд" if remaining_time > 0 else f"Счет: {self.score}, Закончите обьезжать машины", True, (0, 0, 0))
        self.screen.blit(text, (self.screen.get_width() - 400, 10) if remaining_time > 0 else (self.screen.get_width() - 500, 10))

        if remaining_time <= 0:
            self.game_over = True

        self.clock.tick(30)
        if self.game_over:
            if self.Bus.rect.x > self.screen.get_width():
                self.Unload()
            if len(self.moving_cars) == 0 and len(self.parked_cars) == 0:
                self.Bus.rect.x += 20
            else:
                return

        if len(self.moving_cars) == 0 and not self.game_over:
            self.create_moving_cars()
        if len(self.parked_cars) == 0 and not self.game_over:
            self.create_parked_cars()


    def Unload(self):
        if self.render in rules:
            rules.remove(self.render)

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