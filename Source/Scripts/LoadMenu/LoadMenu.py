import os
import pathlib
import shutil
import time
import pygame
from pathlib import Path
from Shared.LM import Level, Memorial
from Shared.SharedFunctions import switch

from DBManager.DBManager import DBManager

rules, events, levels, game_state = [None] * 4


class LoadMenu:
    def __init__(self):
        self.map = None
        self.screen = pygame.Surface
        self.levels = list
        self.font = None
        self.scroll_offset = int
        self.scroll_speed = 30
        self.button_width = 300
        self.button_height = 60
        self.column_widths = [250, 400, 400, 300]
        self.headers = ["Имя файла", "Дата создания", "Дата изменения", "Действие"]
        self.row_height = 150

    def exec(self):
        global rules, events, levels, game_state
        from Globals.Variables import rules, events, levels, game_state
        self.screen = pygame.display.set_mode((1600, 720))
        pygame.display.set_caption('Загрузка уровня')
        self.levels = []
        self.font = pygame.font.Font('../Media/Pangolin-Regular.ttf', 26)
        self.scroll_offset = 0
        self.LoadLevels()

    def LoadLevels(self):
        for level in Path('Levels').glob('*.level'):
            file_name = level.name
            creation_time = level.stat().st_ctime
            modification_time = level.stat().st_mtime
            creation_time_str = time.ctime(creation_time)
            modification_time_str = time.ctime(modification_time)
            save_file = Path('Saves') / f"{Path(file_name).stem}.sqlite"
            has_save = save_file.exists()
            self.levels.append((file_name, creation_time_str, modification_time_str, level, has_save))
        if self.levels:
            events.append(self.TableInteractEvent)
            rules.append(self.render)
        else:
            self.screen.fill((255, 255, 255))
            text_surface = self.font.render('Отсутствуют уровни. Добавьте их в папку Levels и перезапустите программу.',
                                            True, (0, 0, 0))
            rules.append(lambda: self.screen.blit(text_surface, (0, 450)))

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''
        for word in words:
            if not word:
                continue
            test_line = current_line + ' ' + word if current_line else word
            test_width, _ = font.size(test_line)
            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                while word:
                    part = ''
                    for char in word:
                        test_part = part + char
                        test_part_width, _ = font.size(test_part)
                        if test_part_width <= max_width:
                            part = test_part
                        else:
                            break
                    lines.append(part)
                    word = word[len(part):]
                current_line = ''
        if current_line:
            lines.append(current_line)
        return lines

    def render(self):
        self.screen.fill((30, 30, 30))
        for i, header in enumerate(self.headers):
            text_surface = self.font.render(header, True, (255, 255, 255))
            self.screen.blit(text_surface, (50 + sum(self.column_widths[:i]), 50))
        for row, level_data in enumerate(self.levels):
            row_y = 100 + row * self.row_height - self.scroll_offset
            if row_y < 100 or row_y > self.screen.get_height():
                continue
            file_name = level_data[0]
            wrapped_text = self.wrap_text(file_name, self.font, self.column_widths[0])
            for i, line in enumerate(wrapped_text):
                text_surface = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(text_surface, (50, row_y + i * 30))
            for col, data in enumerate(level_data[1:3]):
                text_surface = self.font.render(data, True, (255, 255, 255))
                self.screen.blit(text_surface, (50 + sum(self.column_widths[:col + 1]), row_y))
            button_x = 50 + sum(self.column_widths[:3])
            button_y = row_y - 10
            if level_data[4]:
                pygame.draw.rect(self.screen, (0, 200, 0), (button_x, button_y, self.button_width, self.button_height))
                text_surface = self.font.render("Загрузить сохранение", True, (255, 255, 255))
                text_rect = text_surface.get_rect(
                    center=(button_x + self.button_width // 2, button_y + self.button_height // 2))
                self.screen.blit(text_surface, text_rect)
                button_y += self.button_height + 10
                pygame.draw.rect(self.screen, (128, 50, 255),
                                 (button_x, button_y, self.button_width, self.button_height))
                text_surface = self.font.render("Играть без сохранения", True, (255, 255, 255))
                text_rect = text_surface.get_rect(
                    center=(button_x + self.button_width // 2, button_y + self.button_height // 2))
                self.screen.blit(text_surface, text_rect)
            else:
                pygame.draw.rect(self.screen, (0, 128, 255),
                                 (button_x, button_y, self.button_width, self.button_height))
                text_surface = self.font.render("Загрузить", True, (255, 255, 255))
                text_rect = text_surface.get_rect(
                    center=(button_x + self.button_width // 2, button_y + self.button_height // 2))
                self.screen.blit(text_surface, text_rect)

    def TableInteractEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.scroll_offset = max(self.scroll_offset - self.scroll_speed, 0)
            if event.button == 5:
                max_scroll = max(len(self.levels) * self.row_height - self.screen.get_height() + 150, 0)
                self.scroll_offset = min(self.scroll_offset + self.scroll_speed, max_scroll)
            if event.button == 1:
                self.HandleButtonClick(pygame.mouse.get_pos())

    def HandleButtonClick(self, mouse_pos):
        button_x = 50 + sum(self.column_widths[:3])
        for row, level_data in enumerate(self.levels, start=1):
            row_y = 100 + (row - 1) * self.row_height - self.scroll_offset - 10
            if level_data[4]:
                if (button_x <= mouse_pos[0] <= button_x + self.button_width and row_y <= mouse_pos[
                    1] <= row_y + self.button_height):
                    self.OnLoadSaveButtonClick(level_data[3])
                row_y += self.button_height + 10
                if (button_x <= mouse_pos[0] <= button_x + self.button_width and row_y <= mouse_pos[
                    1] <= row_y + self.button_height):
                    self.OnLoadButtonClick(level_data[3])
            else:
                if (button_x <= mouse_pos[0] <= button_x + self.button_width and row_y <= mouse_pos[
                    1] <= row_y + self.button_height):
                    self.OnLoadButtonClick(level_data[3])

    def OnLoadSaveButtonClick(self, file_path):
        self.LoadLevel(file_path)
        db = DBManager(Path('Saves') / f"{Path(file_path).stem}.sqlite")
        db.load_all()
        db.close()
        del db
        self.Unload()
        switch(self, game_state.gameclasses.MainMenu, self.screen)

    def OnLoadButtonClick(self, file_path):
        print(f"Загрузка уровня {file_path}")
        self.LoadLevel(file_path)
        self.Unload()
        switch(self, game_state.gameclasses.MainMenu, self.screen)

    def LoadLevel(self, file_path):
        if os.path.exists('Temp'): shutil.rmtree('Temp')
        os.mkdir('Temp')
        shutil.unpack_archive(file_path, 'Temp', 'zip')
        game_state.name = '.'.join(pathlib.PurePath(file_path).name.split('.')[:-1])
        level_id = 1
        mem_id = 1
        for item in Path('Temp').iterdir():
            if item.is_dir():
                with open(os.path.join(os.getcwd(), item, 'info.txt'), 'r', encoding='UTF-8') as f:
                    level = Level()
                    level.name, level.desc, level.dotpos = f.readlines()
                    level.name = level.name.strip('\n')
                    level.desc = level.desc.strip('\n')
                    level.id = level_id
                    level.dotpos = list(map(int, level.dotpos.split()))
                for img in Path(os.path.join(item, 'images')).iterdir():
                    level.images.append(pygame.image.load(img).convert())
                for memorial in Path(os.path.join(item, 'memorials')).iterdir():
                    mem = Memorial()
                    mem.id = mem_id
                    mem_id += 1
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
                level_id += 1
                levels.append(level)

    def Unload(self):
        if self.TableInteractEvent in events:
            events.remove(self.TableInteractEvent)
        if self.render in rules:
            rules.remove(self.render)
