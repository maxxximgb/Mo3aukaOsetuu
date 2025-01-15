import os.path

import pygame
from LMClass.LM import Level, Memorial
from Globals.Variables import rules, levels, events, game_state
from pathlib import Path
from CarsMiniGame.CarsMiniGame import CarsMiniGame
from CityScreen.CityScreen import CityScreen


class MainMenu:
    def __init__(self):
        self.screen = pygame.Surface
        self.map = pygame.Surface
        self.entrypoint = []
        pygame.display.set_caption('Главное Меню')
        self.load()

    def load(self):
        with open("Temp/ep.pos") as f:
            self.entrypoint = list(map(int, f.read().split()))
        self.map = pygame.image.load("Temp/map.png").convert()
        self.screen = pygame.display.set_mode(self.map.get_size())
        rules.append(self.draw)
        events.append(self.mouseClickEvent)

    def draw(self):
        self.screen.blit(self.map, (0, 0))
        for l in levels:
            pygame.draw.circle(self.screen, (255, 0, 0) if not l.completed else (0, 255, 0), tuple(l.dotpos), 10, 0)
        pygame.draw.circle(self.screen, (0, 0, 255), tuple(self.entrypoint), 10, 0)

    def mouseClickEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for level in levels:
                    if tuple(level.dotpos)[0] - 10 <= pygame.mouse.get_pos()[0] <= tuple(level.dotpos)[0] + 10 and \
                            tuple(level.dotpos)[1] - 10 <= pygame.mouse.get_pos()[1] <= tuple(level.dotpos)[1] + 10:
                        self.Unload()
                        if not game_state.currentlvl:
                            game_state.currentlvl = level
                            CarsMiniGame(level)
                        elif level == game_state.currentlvl:
                            CityScreen(level)
                        else:
                            game_state.currentlvl = level
                            CarsMiniGame(level)

    def Unload(self):
        if self.draw in rules: rules.remove(self.draw)
