import pygame
from Globals.SharedFunctions import resize_image
from MemorialScreen.MemorialScreen import MemorialScreen
from Globals.SharedFunctions import switch

rules, events, game_state = [None] * 3

class Selector:
    def __init__(self):
        self.memorials = list
        self.screen = pygame.Surface
        self.base_font_size = int
        self.font = pygame.font.Font
        self.resized_previews = list
        self.hovered_index = None
        self.button_font = pygame.font.Font
        self.button_rect = pygame.Rect

    def exec(self):
        global rules, events, game_state
        from Globals.Variables import rules, events, game_state
        self.memorials = game_state.currentlvl.memorials
        self.screen = pygame.display.set_mode((1600, 920))
        self.base_font_size = 36
        self.font = pygame.font.Font(None, self.base_font_size)
        self.resized_previews = [resize_image(p.preview, 300, 300) for p in self.memorials]
        self.hovered_index = None
        self.button_font = pygame.font.Font("../Media/Pangolin-Regular.ttf", 36)
        self.button_rect = pygame.Rect(1600 - 200 - 20, 920 - 60 - 20, 200, 60)
        self.addRules()

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width, _ = font.size(test_line)
            if test_width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        return lines

    def render(self):
        self.screen.fill((255, 255, 255))
        padding = 20
        text_height = 40
        img_width, img_height = self.resized_previews[0].get_width(), self.resized_previews[0].get_height()
        images_per_row = (self.screen.get_width() - padding) // (img_width + padding)
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_index = None

        for i, (resized_image, memorial) in enumerate(zip(self.resized_previews, self.memorials)):
            row = i // images_per_row
            col = i % images_per_row
            x = col * (img_width + padding) + padding
            y = row * (img_height + text_height + padding) + padding

            if x <= mouse_pos[0] <= x + img_width and y <= mouse_pos[1] <= y + img_height:
                self.hovered_index = i
                pygame.draw.rect(self.screen, (255, 0, 0), (x - 5, y - 5, img_width + 10, img_height + 10), 5)

            self.screen.blit(resized_image, (x, y))

            text = memorial.name
            font_size = self.base_font_size
            while True:
                font = pygame.font.Font(None, font_size)
                wrapped_text = self.wrap_text(text, font, img_width)
                total_text_height = len(wrapped_text) * font.get_height()
                if total_text_height <= text_height and font.size(wrapped_text[0])[0] <= img_width:
                    break
                font_size -= 1

            for line_num, line in enumerate(wrapped_text):
                text_surface = font.render(line, True, (0, 0, 0))
                text_x = x + (img_width - text_surface.get_width()) // 2
                text_y = y + img_height + 10 + line_num * font.get_height()
                self.screen.blit(text_surface, (text_x, text_y))

        button_surface = self.button_font.render("Назад", True, (255, 255, 255))
        pygame.draw.rect(self.screen, (0, 128, 0), self.button_rect)
        self.screen.blit(button_surface, (self.button_rect.x + (self.button_rect.width - button_surface.get_width()) // 2, self.button_rect.y + (self.button_rect.height - button_surface.get_height()) // 2))

    def MouseClickEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered_index is not None:
                self.ShowObj(self.memorials[self.hovered_index])
            elif self.button_rect.collidepoint(event.pos):
                self.toScreen()

    def Unload(self):
        if self.MouseClickEvent in events: events.remove(self.MouseClickEvent)
        if self.render in rules: rules.remove(self.render)

    def toScreen(self):
        self.Unload()
        switch(self, game_state.gameclasses.CityScreen, self.screen)

    def addRules(self):
        pygame.display.set_caption('Выбор объекта')
        events.append(self.MouseClickEvent)
        rules.append(self.render)

    def ShowObj(self, memorial):
        self.Unload()
        game_state.currentobj = memorial
        switch(self, game_state.gameclasses.MemorialScreen, self.screen)