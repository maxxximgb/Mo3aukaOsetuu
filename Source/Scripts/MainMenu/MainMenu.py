import pygame
from Globals.Globals import rules # Импорт списка с правилами

class MainMenu:
    def __init__(self):
        self.map = None
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption('Главное Меню')
        self.levels = []
        self.LoadMap()
        self.LoadLevels()

    def LoadMap(self):
        self.screen.fill((255, 255, 255))
        self.map = pygame.image.load("../Images/Map.png")
        rules.append(self.RenderMap) # Пример добавления правила

    def RenderMap(self):
        self.screen.blit(self.map, (0, 0))

    def LoadLevels(self):
        pass