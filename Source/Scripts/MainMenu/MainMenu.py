import os.path
import pygame
import time
from Shared.LM import Level, Memorial
from pathlib import Path
from Shared.SharedFunctions import switch
from DBManager.DBManager import DBManager

rules, levels, events, game_state = [None] * 4

class MainMenu:
    def __init__(self):
        self.saveBtn = pygame.Rect
        self.screen = pygame.Surface
        self.map = pygame.Surface
        self.entrypoint = list
        self.font = pygame.font.Font
        self.initialized = False
        self.save_message = None
        self.save_message_start_time = 0
        self.is_saving = False

    def exec(self):
        global rules, levels, events, game_state
        from Globals.Variables import rules, levels, events, game_state
        self.entrypoint = list()
        pygame.display.set_caption('Главное Меню')
        if not self.initialized:
            self.load()
        self.screen = pygame.display.set_mode((self.map.get_width(), self.map.get_height() + 100))
        self.saveBtn = pygame.Rect(0, self.screen.get_height() - 100, self.screen.get_width(), 100)
        rules.append(self.render)
        events.append(self.mouseClickEvent)
        self.load()

    def load(self):
        with open("Temp/ep.pos") as f:
            self.entrypoint = list(map(int, f.read().split()))
        self.font = pygame.font.Font('../Media/Pangolin-Regular.ttf', 30)
        self.map = pygame.image.load("Temp/map.png").convert()
        self.initialized = True

    def render(self):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.map, (0, 0))
        pygame.draw.circle(self.screen, (255, 0, 0), self.entrypoint if not game_state.currentlvl else game_state.currentlvl.dotpos, 13)
        for l in levels:
            if all([m.completed for m in l.memorials]):
                pygame.draw.circle(self.screen, (0, 255, 0), tuple(l.dotpos), 10, 0)
            elif any([m.completed for m in l.memorials]):
                pygame.draw.circle(self.screen, (0, 255, 255), tuple(l.dotpos), 10, 0)
            elif l == game_state.currentlvl:
                pygame.draw.circle(self.screen, (255, 255, 0), tuple(l.dotpos), 10, 0)
            else:
                pygame.draw.circle(self.screen, (255, 0, 0), tuple(l.dotpos), 10, 0)
        pygame.draw.circle(self.screen, (0, 0, 255), tuple(self.entrypoint), 10, 0)
        self.screen.blit(self.font.render(f"Счет: {game_state.score}", True, (0, 0, 0)), (0, 0))

        if self.is_saving:
            if self.save_message and (time.time() - self.save_message_start_time) < 2:
                message_text = self.font.render(self.save_message, True, (0, 0, 0))
                message_rect = message_text.get_rect(center=(self.screen.get_width() // 2, self.saveBtn.centery))
                self.screen.blit(message_text, message_rect)
            else:
                self.is_saving = False
                self.save_message = None
        else:
            pygame.draw.rect(self.screen, (0, 128, 255), self.saveBtn)
            btn_text = self.font.render("Сохранить", True, (255, 255, 255))
            self.screen.blit(btn_text, btn_text.get_rect(center=self.saveBtn.center))

    def mouseClickEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for level in levels:
                    if tuple(level.dotpos)[0] - 10 <= pygame.mouse.get_pos()[0] <= tuple(level.dotpos)[0] + 10 and \
                            tuple(level.dotpos)[1] - 10 <= pygame.mouse.get_pos()[1] <= tuple(level.dotpos)[1] + 10:
                        self.Unload()
                        if level == game_state.currentlvl:
                            switch(self, game_state.gameclasses.CityScreen, self.screen)
                        else:
                            sound = pygame.mixer.Sound("../Media/busswitch.mp3")
                            sound.play()
                            while pygame.mixer.get_busy():
                                pygame.time.delay(10)

                            game_state.currentlvl = level
                            switch(self, game_state.gameclasses.CarsMiniGame, self.screen, fade_speed=20)
                if self.saveBtn.collidepoint(event.pos):
                    if not os.path.exists('Saves'): os.mkdir('Saves')
                    open(f"Saves/{game_state.name}.sqlite", 'w').close()
                    db = DBManager(f"Saves/{game_state.name}.sqlite")
                    db.save_all()
                    db.close()
                    del db

    def mouseClickEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for level in levels:
                    if tuple(level.dotpos)[0] - 10 <= pygame.mouse.get_pos()[0] <= tuple(level.dotpos)[0] + 10 and \
                            tuple(level.dotpos)[1] - 10 <= pygame.mouse.get_pos()[1] <= tuple(level.dotpos)[1] + 10:
                        self.Unload()
                        if level == game_state.currentlvl:
                            switch(self, game_state.gameclasses.CityScreen, self.screen)
                        else:
                            sound = pygame.mixer.Sound("../Media/busswitch.mp3")
                            sound.play()
                            while pygame.mixer.get_busy():
                                pygame.time.delay(10)

                            game_state.currentlvl = level
                            switch(self, game_state.gameclasses.CarsMiniGame, self.screen, fade_speed=20)
                if self.saveBtn.collidepoint(event.pos):
                    self.is_saving = True
                    self.save_message = 'Сохранение'
                    self.save_message_start_time = time.time()
                    if not os.path.exists('Saves'): os.mkdir('Saves')
                    open(f"Saves/{game_state.name}.sqlite", 'w').close()
                    db = DBManager(f"Saves/{game_state.name}.sqlite")
                    db.save_all()
                    db.close()
                    self.save_message = 'Успешно сохранено'
                    self.save_message_start_time = time.time()

    def Unload(self):
        if self.render in rules: rules.remove(self.render)
        if self.mouseClickEvent in events: events.remove(self.mouseClickEvent)