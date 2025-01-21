import sys
import pygame
from Shared.SharedFunctions import switch

game_state, levels, rules, events = [None] * 4

def seconds_to_hms(seconds):
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds %= 60
    return f"{hours:02}:{minutes:02}:{int(seconds):02}"

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        test_surface = font.render(test_line, True, (0, 0, 0))
        if test_surface.get_width() <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))
    return lines


class EndWindow:
    def __init__(self):
        self.mintime = str
        self.maxtime = str
        self.averagetime = str
        self.screen = pygame.Surface
        self.font = pygame.font.Font
        self.uncompleted = list
        self.completed = str
        self.puzzles_completed = int
        self.backBtn = pygame.Rect
        self.exitBtn = pygame.Rect

    def exec(self):
        global game_state, levels, rules, events
        from Globals.Variables import game_state, levels, rules, events
        self.puzzles_completed = 0
        self.uncompleted = list()
        self.font = pygame.font.Font('../Media/Pangolin-Regular.ttf', 25)
        for level in levels:
            if not level.completed:
                self.uncompleted.append([level, []])
            for memorial in level.memorials:
                if not memorial.completed:
                    self.uncompleted[-1][-1].append(memorial)
                else:
                    self.puzzles_completed += 1

        if not self.uncompleted:
            self.completed = 'Поздравляем, игра пройдена!'
            self.averagetime = seconds_to_hms(sum(game_state.puzzletime) / len(game_state.puzzletime))
            self.maxtime = seconds_to_hms(max(game_state.puzzletime))
            self.mintime = seconds_to_hms(min(game_state.puzzletime))
        else:
            self.completed = 'Игра пройдена не полностью.'

        self.screen = pygame.display.set_mode((1280, 720))
        self.backBtn = pygame.Rect(self.screen.get_width() - 250, self.screen.get_height() - 100, 200, 50)
        self.exitBtn = pygame.Rect(self.screen.get_width() - 250, self.screen.get_height() - 180, 200, 50)

        events.append(self.mouseClickEvent)

    def render(self):
        self.screen.fill((255, 255, 255))
        y_offset = 80
        pygame.draw.rect(self.screen, (0, 128, 225), self.backBtn)
        pygame.draw.rect(self.screen, (255, 25, 25), self.exitBtn)
        text_surface = self.font.render('Назад', True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.backBtn.center)
        self.screen.blit(text_surface, text_rect)
        text_surface = self.font.render('Выход', True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.exitBtn.center)
        self.screen.blit(text_surface, text_rect)
        for line in wrap_text(self.completed, self.font, self.screen.get_width()):
            text_surface = self.font.render(line, True, (0, 0, 0))
            text_rect = text_surface.get_rect(centerx=self.screen.get_rect().centerx)
            self.screen.blit(text_surface, text_rect)
            y_offset += text_rect.height + 5

        if self.uncompleted:
            self.screen.blit(self.font.render('Не пройденые уровни: ', True, (0, 0, 0)), (40, 80))
        else:
            text_surface = self.font.render(f'Счет: {game_state.score}', True, (0, 0, 0))
            self.screen.blit(text_surface, (40, y_offset))
            y_offset += text_surface.get_rect().height + 5
            text_surface = self.font.render(f'Уровней пройдено: {len(levels)}', True, (0, 0, 0))
            self.screen.blit(text_surface, (40, y_offset))
            y_offset += text_surface.get_rect().height + 5
            text_surface = self.font.render(f'Пазлов собрано: {self.puzzles_completed}', True, (0, 0, 0))
            self.screen.blit(text_surface, (40, y_offset))
            y_offset += text_surface.get_rect().height + 5
            text_surface = self.font.render(f'Поездок в игре с машинами: {game_state.car_trips}', True, (0, 0, 0))
            self.screen.blit(text_surface, (40, y_offset))
            y_offset += text_surface.get_rect().height + 5
            text_surface = self.font.render(f'Аварий в игре с машинами: {game_state.car_faults}', True, (0, 0, 0))
            self.screen.blit(text_surface, (40, y_offset))
            y_offset += text_surface.get_rect().height + 5
            text_surface = self.font.render(f'Среднее время сборки пазла: {self.averagetime}', True, (0, 0, 0))
            self.screen.blit(text_surface, (40, y_offset))
            y_offset += text_surface.get_rect().height + 5
            text_surface = self.font.render(f'Максимальное время сборки пазла: {self.maxtime}', True, (0, 0, 0))
            self.screen.blit(text_surface, (40, y_offset))
            y_offset += text_surface.get_rect().height + 5
            text_surface = self.font.render(f'Минимальное время сборки пазла: {self.maxtime}', True, (0, 0, 0))
            self.screen.blit(text_surface, (40, y_offset))
            y_offset += text_surface.get_rect().height + 5
        for level, memorials in self.uncompleted:
            txt = f"{level.name}: {', '.join(m.name for m in memorials)}" if memorials else None
            if not txt:
                continue

            for line in wrap_text(txt, self.font, self.screen.get_width() - 80):
                text_surface = self.font.render(line, True, (0, 0, 0))
                self.screen.blit(text_surface, (40, y_offset))
                y_offset += text_surface.get_rect().height + 5

    def mouseClickEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.backBtn.collidepoint(pygame.mouse.get_pos()):
                self.Unload()
                switch(self, game_state.gameclasses.MainMenu, self.screen)
            elif self.exitBtn.collidepoint(pygame.mouse.get_pos()):
                self.Unload()
                pygame.quit()
                sys.exit()

    def Unload(self):
        if self.render in rules: rules.remove(self.render)
        if self.mouseClickEvent in events: events.remove(self.mouseClickEvent)

