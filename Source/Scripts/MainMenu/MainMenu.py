import os.path
import pygame
from SharedClasses.LM import Level, Memorial
from pathlib import Path
from Globals.SharedFunctions import switch

rules, levels, events, game_state = [None] * 4

class MainMenu:
    def __init__(self):
        self.screen = pygame.Surface
        self.map = pygame.Surface
        self.entrypoint = list
        self.initialized = False

    def exec(self):
        global rules, levels, events, game_state
        from Globals.Variables import rules, levels, events, game_state
        self.entrypoint = list()
        pygame.display.set_caption('Главное Меню')
        if not self.initialized:
            self.load()
        self.screen = pygame.display.set_mode(self.map.get_size())
        rules.append(self.render)
        events.append(self.mouseClickEvent)
        self.load()

    def load(self):
        with open("Temp/ep.pos") as f:
            self.entrypoint = list(map(int, f.read().split()))
        self.map = pygame.image.load("Temp/map.png").convert()
        self.initialized = True

    def render(self):
        self.screen.blit(self.map, (0, 0))
        for l in levels:
            if l.completed:
                pygame.draw.circle(self.screen,(0, 255, 0), tuple(l.dotpos), 10, 0)
            elif l == game_state.currentlvl:
                pygame.draw.circle(self.screen, (255, 255, 0) , tuple(l.dotpos), 10, 0)
            else:
                pygame.draw.circle(self.screen, (255, 0, 0), tuple(l.dotpos), 10, 0)
        pygame.draw.circle(self.screen, (0, 0, 255), tuple(self.entrypoint), 10, 0)

    def mouseClickEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for level in levels:
                    if tuple(level.dotpos)[0] - 10 <= pygame.mouse.get_pos()[0] <= tuple(level.dotpos)[0] + 10 and \
                            tuple(level.dotpos)[1] - 10 <= pygame.mouse.get_pos()[1] <= tuple(level.dotpos)[1] + 10:
                        self.Unload()
                        if level != game_state.currentlvl:
                            game_state.currentlvl = level
                            switch(self, game_state.gameclasses.CityScreen, self.screen)
                        else:
                            sound = pygame.mixer.Sound("../Media/busswitch.mp3")
                            sound.play()
                            while pygame.mixer.get_busy():
                                pygame.time.delay(10)

                            game_state.currentlvl = level
                            switch(self, game_state.gameclasses.CarsMiniGame, self.screen, fade_speed=20)

    def Unload(self):
        if self.render in rules: rules.remove(self.render)
        if self.mouseClickEvent in events: events.remove(self.mouseClickEvent)