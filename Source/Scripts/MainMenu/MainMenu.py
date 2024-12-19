import pygame
from Globals.Globals import rules # Импорт списка с правилами

class MainMenu:
    def __init__(self):
        self.map = None
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption('Главное Меню')
        self.levels = []
        self.LoadLevels()

    def LoadLevels(self):
        pass

    def Unload(self):
        rules.remove(self.RenderMap)