import pygame
from Globals.Globals import rules, game_state, events
from Globals.SharedFunctions import resize_image, get_aspect_ratio
from MemorialScreen.Selector import Selector


class CityScreen:
    def __init__(self, level):
        self.level = level
        self.screen = pygame.display.set_mode((1600, 920))
        pygame.display.set_caption(self.level.name)
        self.grid = self.create_grid()
        rules.append(self.render)
        self.font_path = "../Media/Pangolin-Regular.ttf"
        self.name_font = pygame.font.Font(self.font_path, 48)
        self.desc_font = pygame.font.Font(self.font_path, 36)
        self.button_font = pygame.font.Font(self.font_path, 36)
        self.button_width = 200
        self.button_height = 60
        self.button_x = 1600 - self.button_width - 20
        self.button_y = 920 - self.button_height - 20
        self.button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        events.append(self.nextbtnclick)

    def create_grid(self):
        num_images = len(self.level.images)
        grid = []
        max_grid_width = 700
        max_grid_height = 700
        padding = 10
        bottom_padding = 5

        if num_images == 1:
            img = self.level.images[0]
            resized_img = resize_image(img, max_grid_width, max_grid_height)
            grid.append((resized_img, (0, 0)))

        elif num_images == 2:
            img1, img2 = self.level.images
            if get_aspect_ratio(img1) > 1 and get_aspect_ratio(img2) > 1:
                img1 = resize_image(img1, max_grid_width, max_grid_height // 2 - bottom_padding // 2)
                img2 = resize_image(img2, max_grid_width, max_grid_height // 2 - bottom_padding // 2)
                grid.append((img1, (0, 0)))
                grid.append((img2, (0, max_grid_height // 2 + bottom_padding // 2)))
            elif get_aspect_ratio(img1) < 1 and get_aspect_ratio(img2) < 1:
                img1 = resize_image(img1, max_grid_width // 2 - padding // 2, max_grid_height)
                img2 = resize_image(img2, max_grid_width // 2 - padding // 2, max_grid_height)
                grid.append((img1, (0, 0)))
                grid.append((img2, (max_grid_width // 2 + padding // 2, 0)))
            else:
                if get_aspect_ratio(img1) > 1:
                    img1 = resize_image(img1, max_grid_width, max_grid_height // 2 - bottom_padding // 2)
                    img2 = resize_image(img2, max_grid_width, max_grid_height // 2 - bottom_padding // 2)
                else:
                    img1 = resize_image(img1, max_grid_width // 2 - padding // 2, max_grid_height)
                    img2 = resize_image(img2, max_grid_width // 2 - padding // 2, max_grid_height)
                grid.append((img1, (0, 0)))
                grid.append((img2, (img1.get_width() + padding, 0)))

        elif num_images == 3:
            ratios = [get_aspect_ratio(img) for img in self.level.images]
            vertical_count = sum(ratio < 1 for ratio in ratios)

            if vertical_count == 0:
                img1 = resize_image(self.level.images[0], max_grid_width // 2 - padding // 2, max_grid_height // 2 - bottom_padding // 2)
                img2 = resize_image(self.level.images[1], max_grid_width // 2 - padding // 2, max_grid_height // 2 - bottom_padding // 2)
                img3 = resize_image(self.level.images[2], max_grid_width, max_grid_height // 2 - bottom_padding // 2)
                grid.append((img1, (0, 0)))
                grid.append((img2, (max_grid_width // 2 + padding // 2, 0)))
                grid.append((img3, ((max_grid_width - img3.get_width()) // 2, max_grid_height // 2 - 30 + bottom_padding // 2)))
            elif vertical_count == 1:
                vertical_img = self.level.images[ratios.index(min(ratios))]
                horizontal_imgs = [img for img in self.level.images if img != vertical_img]
                vertical_img = resize_image(vertical_img, max_grid_width // 2 - padding // 2, max_grid_height)
                img1 = resize_image(horizontal_imgs[0], max_grid_width // 2 - padding // 2, max_grid_height // 2 - bottom_padding // 2)
                img2 = resize_image(horizontal_imgs[1], max_grid_width // 2 - padding // 2, max_grid_height // 2 - bottom_padding // 2)
                grid.append((vertical_img, (0, 0)))
                grid.append((img1, (max_grid_width // 2 + padding // 2, 0)))
                grid.append((img2, (max_grid_width // 2 + padding // 2, max_grid_height // 2 + bottom_padding // 2)))
            elif vertical_count == 2:
                horizontal_img = self.level.images[ratios.index(max(ratios))]
                vertical_imgs = [img for img in self.level.images if img != horizontal_img]
                horizontal_img = resize_image(horizontal_img, max_grid_width, max_grid_height // 2 - bottom_padding // 2)
                img1 = resize_image(vertical_imgs[0], max_grid_width // 2 - padding // 2, max_grid_height // 2 - bottom_padding // 2)
                img2 = resize_image(vertical_imgs[1], max_grid_width // 2 - padding // 2, max_grid_height // 2 - bottom_padding // 2)
                grid.append((img1, (0, 0)))
                grid.append((img2, (max_grid_width // 2 + padding // 2, 0)))
                grid.append((horizontal_img, ((max_grid_width - horizontal_img.get_width()) // 2, max_grid_height // 2 + bottom_padding // 2)))
            else:
                img1 = resize_image(self.level.images[0], max_grid_width // 2 - padding // 2, max_grid_height // 2 - bottom_padding // 2)
                img2 = resize_image(self.level.images[1], max_grid_width // 2 - padding // 2, max_grid_height // 2 - bottom_padding // 2)
                img3 = resize_image(self.level.images[2], max_grid_width, max_grid_height // 2 - bottom_padding // 2)
                grid.append((img1, (0, 0)))
                grid.append((img2, (max_grid_width // 2 + padding // 2, 0)))
                grid.append((img3, ((max_grid_width - img3.get_width()) // 2, max_grid_height // 2 + bottom_padding // 2)))

        elif num_images == 4:
            img1 = resize_image(self.level.images[0], max_grid_width // 2 - padding // 2, max_grid_height // 2 - bottom_padding // 2)
            img2 = resize_image(self.level.images[1], max_grid_width // 2 - padding // 2, max_grid_height // 2 - bottom_padding // 2)
            img3 = resize_image(self.level.images[2], max_grid_width // 2 - padding // 2, max_grid_height // 2 - bottom_padding // 2)
            img4 = resize_image(self.level.images[3], max_grid_width // 2 - padding // 2, max_grid_height // 2 - bottom_padding // 2)
            grid.append((img1, (0, 0)))
            grid.append((img2, (max_grid_width // 2 + padding // 2, 0)))
            grid.append((img3, (0, max_grid_height // 2 + bottom_padding // 2)))
            grid.append((img4, (max_grid_width // 2 + padding // 2, max_grid_height // 2 + bottom_padding // 2)))

        return grid

    def render(self):
        self.screen.fill((255, 255, 255))
        for img, pos in self.grid:
            self.screen.blit(img, pos)

        right_boundary = max([pos[0] + img.get_width() for img, pos in self.grid]) if self.grid else 0
        text_x = right_boundary + 10
        text_y = 10

        name_surface = self.name_font.render(self.level.name, True, (0, 0, 0))
        self.screen.blit(name_surface, (text_x, text_y))

        desc_lines = self.wrap_text(self.level.desc, self.desc_font, 1600 - text_x - 10)
        for i, line in enumerate(desc_lines):
            desc_surface = self.desc_font.render(line, True, (0, 0, 0))
            self.screen.blit(desc_surface, (text_x, text_y + 50 + i * 30))

        button_text = "Далее"
        button_surface = self.button_font.render(button_text, True, (255, 255, 255))

        pygame.draw.rect(self.screen, (0, 128, 0), self.button_rect)
        text_x_pos = self.button_x + (self.button_width - button_surface.get_width()) // 2
        text_y_pos = self.button_y + (self.button_height - button_surface.get_height()) // 2
        self.screen.blit(button_surface, (text_x_pos, text_y_pos))

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''

        for word in words:
            test_line = current_line + ' ' + word if current_line else word
            test_width, _ = font.size(test_line)

            if test_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def to_mem(self):
        self.Unload()
        Selector(self.level)

    def nextbtnclick(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if self.button_rect.collidepoint(mouse_pos):
                    self.to_mem()

    def Unload(self):
        if self.render in rules: rules.remove(self.render)
        if self.nextbtnclick in events: events.remove(self.nextbtnclick)