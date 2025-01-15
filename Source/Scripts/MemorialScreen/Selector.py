import pygame
from Globals.SharedFunctions import get_aspect_ratio, resize_image

class Selector:
    def __init__(self, level):
        self.memorials = level.memorials
        self.screen = pygame.display.set_mode((1600, 920))
        pygame.display.set_caption('Выбор объекта')
        self.font = pygame.font.Font(None, 36)
        self.resized_previews = self.load_previews()


    def load_previews(self):
        resized_previews = []
        for preview in [p.preview for p in self.memorials]:
            resized_image = resize_image(preview, 500, 500)
            resized_previews.append(resized_image)

        return resized_previews


    def render(self):
        self.screen.fill((255, 255, 255))
        padding = 20
        text_height = 40
        images_per_row = (self.screen.get_width() - padding) // (self.resized_previews[0].get_width() + padding)

        for i, (resized_image, memorial) in enumerate(zip(self.resized_previews, self.memorials)):
            row = i // images_per_row
            col = i % images_per_row

            x = col * (resized_image.get_width() + padding) + padding
            y = row * (resized_image.get_height() + text_height + padding) + padding

            self.screen.blit(resized_image, (x, y))

            text_surface = self.font.render(memorial.name, True, (0, 0, 0))
            text_x = x + (resized_image.get_width() - text_surface.get_width()) // 2
            text_y = y + resized_image.get_height() + 10
            self.screen.blit(text_surface, (text_x, text_y))