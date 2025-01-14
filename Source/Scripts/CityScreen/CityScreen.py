import pygame
from Globals.Globals import rules, game_state

def get_aspect_ratio(image):
    return image.get_width() / image.get_height()

def resize_image(image, target_width, target_height):
    original_width, original_height = image.get_size()
    original_ratio = original_width / original_height
    target_ratio = target_width / target_height

    if original_ratio > target_ratio:
        new_width = target_width
        new_height = int(target_width / original_ratio)
    else:
        new_height = target_height
        new_width = int(target_height * original_ratio)

    return pygame.transform.scale(image, (new_width, new_height))

class CityScreen:
    def __init__(self, level):
        self.level = level
        self.screen = pygame.display.set_mode((1600, 920))
        pygame.display.set_caption(self.level.name)
        self.font = pygame.font.Font(None, 36)
        self.grid = self.create_grid()
        rules.append(self.render)

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

        name_font = pygame.font.Font(None, 48)
        name_surface = name_font.render(self.level.name, True, (0, 0, 0))
        self.screen.blit(name_surface, (text_x, text_y))

        desc_font = pygame.font.Font(None, 36)
        desc_lines = self.wrap_text(self.level.desc, desc_font, 1600 - text_x - 10)
        for i, line in enumerate(desc_lines):
            desc_surface = desc_font.render(line, True, (0, 0, 0))
            self.screen.blit(desc_surface, (text_x, text_y + 50 + i * 30))

        pygame.display.flip()

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