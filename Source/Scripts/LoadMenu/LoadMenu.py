import os
import shutil
import time
import pygame
from pathlib import Path
from SharedClasses.LM import Level, Memorial
from Globals.SharedFunctions import switch

rules, events, levels, game_state = [None] * 4

class LoadMenu:
    def __init__(self):
        self.map = None
        self.screen = pygame.Surface
        self.levels = list
        self.font = None
        self.scroll_offset = int
        self.scroll_speed = int
        self.button_width = int
        self.button_height = int
        self.button_text = str
        self.column_widths = list
        self.row_height = int

    def exec(self):
        global rules, events, levels, game_state
        from Globals.Variables import rules, events, levels, game_state
        self.map = None
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption('Загрузка уровня')
        self.levels = []
        self.font = pygame.font.Font(None, 36)
        self.scroll_offset = 0
        self.scroll_speed = 20
        self.button_width = 150
        self.button_height = 30
        self.button_text = "Загрузить"
        self.column_widths = [300, 350, 350, 150]
        self.row_height = 40
        self.LoadLevels()

    def LoadLevels(self):
        for level in Path('Levels').glob('*.level'):
            file_name = level.name
            creation_time = level.stat().st_ctime
            modification_time = level.stat().st_mtime
            creation_time_str = time.ctime(creation_time)
            modification_time_str = time.ctime(modification_time)
            self.levels.append((file_name, creation_time_str, modification_time_str, level))
        if self.levels:
            events.append(self.TableInteractEvent)
            rules.append(self.render)
        else:
            self.screen.fill((255, 255, 255))
            font = pygame.font.Font('../Media/Pangolin-Regular.ttf', 39)
            text_surface = font.render('Отсутствуют уровни. Добавьте их в папку Levels и перезапустите программу.', True, (0, 0, 0))
            rules.append(lambda: self.screen.blit(text_surface, (0, 300)))


    def render(self):
        self.screen.fill((30, 30, 30))
        headers = ["Имя файла", "Дата создания", "Дата изменения", "Действие"]

        for i, header in enumerate(headers):
            text_surface = self.font.render(header, True, (255, 255, 255))
            self.screen.blit(text_surface, (50 + sum(self.column_widths[:i]), 50))

        for row, level_data in enumerate(self.levels):
            if (row + 1) * self.row_height - self.scroll_offset < 0:
                continue
            if (row + 1) * self.row_height - self.scroll_offset > self.screen.get_height():
                break

            for col, data in enumerate(level_data[:3]):
                text_surface = self.font.render(data, True, (255, 255, 255))
                self.screen.blit(text_surface,
                                 (50 + sum(self.column_widths[:col]), 100 + row * self.row_height - self.scroll_offset))

            button_x = 50 + sum(self.column_widths[:3])
            button_y = 100 + row * self.row_height - self.scroll_offset
            pygame.draw.rect(self.screen, (0, 128, 255), (button_x, button_y, self.button_width, self.button_height))
            text_surface = self.font.render(self.button_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(
                center=(button_x + self.button_width // 2, button_y + self.button_height // 2))
            self.screen.blit(text_surface, text_rect)

    def TableInteractEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.scroll_offset = max(self.scroll_offset - self.scroll_speed, 0)
            if event.button == 5:
                max_scroll = max(len(self.levels) * self.row_height - self.screen.get_height() + 100, 0)
                self.scroll_offset = min(self.scroll_offset + self.scroll_speed, max_scroll)
            if event.button == 1:
                self.HandleButtonClick(pygame.mouse.get_pos())

    def HandleButtonClick(self, mouse_pos):
        button_x = 50 + sum(self.column_widths[:3])
        for row, level_data in enumerate(self.levels):
            button_y = 100 + row * self.row_height - self.scroll_offset
            if (button_x <= mouse_pos[0] <= button_x + self.button_width and
                    button_y <= mouse_pos[1] <= button_y + self.button_height):
                self.OnLoadButtonClick(level_data[3])

    def OnLoadButtonClick(self, file_path):
        shutil.rmtree('Temp')
        os.mkdir('Temp')
        shutil.unpack_archive(file_path, 'Temp', 'zip')
        for item in Path('Temp').iterdir():
            if item.is_dir():
                with open(os.path.join(os.getcwd(), item, 'info.txt'), 'r', encoding='UTF-8') as f:
                    level = Level()
                    level.name, level.desc, level.dotpos = f.readlines()
                    level.name = level.name.strip('\n')
                    level.desc = level.desc.strip('\n')
                    level.dotpos = list(map(int, level.dotpos.split()))
                for img in Path(os.path.join(item, 'images')).iterdir():
                    level.images.append(pygame.image.load(img).convert())
                for memorial in Path(os.path.join(item, 'memorials')).iterdir():
                    mem = Memorial()
                    with open(os.path.join(memorial, 'info.txt'), 'r', encoding='UTF-8') as m:
                        l = [l.strip('\n') for l in m.readlines()]
                        mem.name, mem.desc = l
                    for img in Path(os.path.join(memorial, 'images')).iterdir():
                        if img.is_file():
                            if img.name.startswith('preview'):
                                mem.preview = pygame.image.load(img).convert()
                            elif img.name.startswith('puzzle'):
                                mem.puzzle = pygame.image.load(img).convert()
                            else:
                                mem.images.append(pygame.image.load(img).convert())
                        else:
                            with open(os.path.join(img, 'matrix.txt'), 'r', encoding='UTF-8') as matrix:
                                mem.puzzlepos.extend([l.strip('\n').split() for l in matrix.readlines()])
                            mem.puzzlePath = str(img)
                    level.memorials.append(mem)
                levels.append(level)
        self.Unload()
        switch(self, game_state.gameclasses.MainMenu, self.screen, fade_speed=10)

    def Unload(self):
        if self.TableInteractEvent in events:
            events.remove(self.TableInteractEvent)
        if self.render in rules:
            rules.remove(self.render)
