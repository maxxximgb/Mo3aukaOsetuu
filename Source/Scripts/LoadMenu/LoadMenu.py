import pygame.gfxdraw
import os
import pathlib
import shutil
import threading
import time
import pygame
from pathlib import Path
import cv2
from Shared.LM import Level, Memorial
from Shared.SharedFunctions import switch
from DBManager.DBManager import DBManager

rules, events, levels, game_state = [None] * 4


def count_steps():
    total_steps = 1
    levels = [item for item in Path(os.path.join(os.getcwd(), 'Temp')).iterdir()
              if item.is_dir() and item.name not in ['ep.pos', 'map.png']]

    total_steps += len(levels)

    for level in levels:
        if level.is_dir():
            images_folder = level / 'images'
            if images_folder.exists():
                level_images = len(list(images_folder.iterdir()))
                total_steps += level_images

            memorials_folder = level / 'memorials'
            if memorials_folder.exists():
                memorials = list(memorials_folder.iterdir())
                total_steps += 2 * len(memorials)

                for memorial in memorials:
                    if memorial.is_dir():
                        mem_images_folder = memorial / 'images'
                        if mem_images_folder.exists():
                            mem_images = len(list(mem_images_folder.iterdir())) - 2
                            total_steps += mem_images
                        total_steps += 1

    return total_steps


class LoadMenu:
    def __init__(self):
        self.anim = LoadAnimation
        self.completed = int
        self.total = int
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
        self.anim = LoadAnimation(save=file_path)
        self.Unload()
        switch(self, self.anim, self.screen)
        self.anim.toggle_type()
        threading.Thread(target=self.LoadLevel, args=[file_path]).start()

    def OnLoadButtonClick(self, file_path):
        self.anim = LoadAnimation()
        self.Unload()
        switch(self, self.anim, self.screen)
        self.anim.toggle_type()
        threading.Thread(target=self.LoadLevel, args=[file_path]).start()

    def LoadLevel(self, file_path):
        self.completed = 0
        self.anim.txt = 'Проверка временной папки'
        if os.path.exists('Temp'):
            shutil.rmtree('Temp')
        os.mkdir('Temp')

        self.anim.txt = 'Распаковка файла уровня'
        shutil.unpack_archive(file_path, 'Temp', 'zip')

        self.total = count_steps()
        self.updateProgress()
        game_state.name = '.'.join(pathlib.PurePath(file_path).name.split('.')[:-1])
        level_id = 1
        mem_id = 1

        for item in Path('Temp').iterdir():
            if item.is_dir():
                self.anim.txt = 'Чтение информации об уровне'
                with open(os.path.join(os.getcwd(), item, 'info.txt'), 'r', encoding='UTF-8') as f:
                    level = Level()
                    level.name, level.desc, level.dotpos = f.readlines()
                    level.name = level.name.strip('\n')
                    level.desc = level.desc.strip('\n')
                    level.id = level_id
                    level.dotpos = list(map(int, level.dotpos.split()))
                self.updateProgress()

                self.anim.txt = f'Чтение картинок уровня {level.name}'
                images_folder = Path(os.path.join(item, 'images'))
                if images_folder.exists():
                    for img in images_folder.iterdir():
                        level.images.append(pygame.image.load(img).convert())
                        self.updateProgress()

                memorials_folder = Path(os.path.join(item, 'memorials'))
                if memorials_folder.exists():
                    for memorial in memorials_folder.iterdir():
                        mem = Memorial()
                        mem.id = mem_id
                        mem_id += 1
                        self.anim.txt = f'Чтение информации о памятнике уровня {level.name}'
                        with open(os.path.join(memorial, 'info.txt'), 'r', encoding='UTF-8') as m:
                            l = [l.strip('\n') for l in m.readlines()]
                            mem.name, mem.desc = l
                        self.updateProgress()

                        self.anim.txt = f'Загрузка картинок памятника {mem.name} уровня {level.name}'
                        mem_images_folder = Path(os.path.join(memorial, 'images'))
                        if mem_images_folder.exists():
                            for img in mem_images_folder.iterdir():
                                if img.is_file():
                                    if img.name.startswith('preview'):
                                        mem.preview = pygame.image.load(img).convert()
                                    elif img.name.startswith('puzzle'):
                                        mem.puzzle = pygame.image.load(img).convert()
                                    else:
                                        mem.images.append(pygame.image.load(img).convert())
                                    self.updateProgress()
                                else:
                                    with open(os.path.join(img, 'matrix.txt'), 'r', encoding='UTF-8') as matrix:
                                        mem.puzzlepos.extend([l.strip('\n').split() for l in matrix.readlines()])
                                    mem.puzzlePath = str(img)
                                    self.updateProgress()

                        level.memorials.append(mem)
                level_id += 1
                levels.append(level)
        self.anim.finish()

    def updateProgress(self):
        self.completed += 1
        self.anim.set_progress((self.completed / self.total) * 100)

    def Unload(self):
        if self.TableInteractEvent in events:
            events.remove(self.TableInteractEvent)
        if self.render in rules:
            rules.remove(self.render)


class LoadAnimation:
    def __init__(self, save=None):
        self.save = save
        self.txt = "Инициализация..."
        self.progress = 0
        self.indeterminate = True
        self.Unloading = False
        self.frame_index = 0
        self.last_update = 0
        self.stripes_offset = 0
        self.finished = False

    def exec(self):
        self.screen = pygame.display.set_mode((1280, 720))
        self.cap = cv2.VideoCapture('../Media/loading.mp4')
        self.gif_frames = self._load_gif()
        self._create_stripes()

    def _create_stripes(self):
        self.stripes = pygame.Surface((300, 20), pygame.SRCALPHA)
        for x in range(300):
            blue = int(255 * (1 - x / 300))
            pygame.draw.line(self.stripes, (blue, blue, 255, 255), (x, 0), (x, 20), 3)
        self.mask = pygame.Surface((300, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.mask, (255, 255, 255, 255), (0, 0, 300, 20), border_radius=10)

    def _load_gif(self):
        cap = cv2.VideoCapture("../Media/loading.gif")
        frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (int(self.cap.get(3) * 0.5), int(self.cap.get(4) * 0.5)))
            frames.append(pygame.surfarray.make_surface(frame))
        cap.release()
        return frames

    def render(self):
        self.screen.fill((255, 255, 255))
        font = pygame.font.Font(None, 36)

        animation_height = self._draw_animation()
        text_bottom = self._draw_text(font, animation_height)
        self._draw_progress_bar(font, text_bottom)

        if self.finished and not self.Unloading:
            self._finalize()


    def _draw_animation(self):
        if self.indeterminate:
            return self._draw_video()
        else:
            return self._draw_gif()

    def _draw_video(self):
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(cv2.resize(frame, (int(self.cap.get(3) * 0.5), int(self.cap.get(4) * 0.5))),
                                 cv2.COLOR_BGR2RGB)
            video_surface = pygame.surfarray.make_surface(cv2.flip(frame, 1))
            video_rect = video_surface.get_rect(
                center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))
            self.screen.blit(video_surface, video_rect)
            return video_rect.bottom
        return self.screen.get_height() // 2

    def _draw_gif(self):
        radius = 100
        if pygame.time.get_ticks() - self.last_update > 100:
            self.frame_index = (self.frame_index + 1) % len(self.gif_frames)
            self.last_update = pygame.time.get_ticks()

        circle_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(circle_surf, (255, 255, 255, 255), (radius, radius), radius)
        gif_frame = pygame.transform.rotate(pygame.transform.scale(self.gif_frames[self.frame_index], (radius, radius)), 270)
        circle_surf.blit(gif_frame, (radius // 2, radius // 2), special_flags=pygame.BLEND_RGBA_MULT)
        circle_rect = circle_surf.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(circle_surf, circle_rect)

        pygame.gfxdraw.arc(self.screen, self.screen.get_width() // 2, self.screen.get_height() // 2,
                           radius, 90, 90 + int(3.6 * self.progress), (0, 0, 255))
        return circle_rect.bottom

    def _draw_text(self, font, start_y):
        lines = []
        current_line = []
        max_width = self.screen.get_width() - 40

        for word in self.txt.split():
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] > max_width:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        if current_line:
            lines.append(' '.join(current_line))

        y = start_y + 20
        for line in lines:
            text = font.render(line, True, (0, 0, 0))
            text_rect = text.get_rect(centerx=self.screen.get_width() // 2, y=y)
            self.screen.blit(text, text_rect)
            y += text.get_height() + 5

        return y

    def _draw_progress_bar(self, font, start_y):
        bar_rect = pygame.Rect(0, start_y + 20, 300, 20)
        bar_rect.centerx = self.screen.get_width() // 2

        pygame.draw.rect(self.screen, (200, 200, 200), bar_rect, border_radius=10)

        if self.indeterminate:
            scroll = pygame.Surface((300, 20), pygame.SRCALPHA)
            self.stripes_offset = (self.stripes_offset - 2) % 300
            scroll.blit(self.stripes, (-self.stripes_offset, 0))
            scroll.blit(self.stripes, (300 - self.stripes_offset, 0))
            scroll.blit(self.mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(scroll, bar_rect.topleft)
        else:
            progress_width = int(300 * (self.progress / 100))
            pygame.draw.rect(self.screen, (0, 0, 255), (bar_rect.x, bar_rect.y, progress_width, 20), border_radius=10)
            text = font.render(f"{int(self.progress)}%", True, (0, 0, 0))
            text_rect = text.get_rect(center=bar_rect.center)
            self.screen.blit(text, text_rect)

    def _finalize(self):
        self.Unloading = True
        self.toggle_type()
        if self.save:
            self.txt = 'Загрузка сохранения'
            a = DBManager(Path('Saves') / f"{Path(self.save).stem}.sqlite")
            a.load_all()
            del a
        if self.render in rules:
            rules.remove(self.render)
        self.txt = 'Переход на карту'
        switch(self, game_state.gameclasses.MainMenu, self.screen)

    def finish(self):
        self.finished = True

    def set_progress(self, value):
        self.progress = value

    def toggle_type(self):
        self.indeterminate = not self.indeterminate
        self.cap.release()
        video_path = '../Media/loading2.mp4' if not self.indeterminate else '../Media/loading.mp4'
        self.cap = cv2.VideoCapture(video_path)