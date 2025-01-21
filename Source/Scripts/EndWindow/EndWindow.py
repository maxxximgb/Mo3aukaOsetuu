import pygame


def split_text_into_lines(text, font, max_width):
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
        self.screen = pygame.Surface
        self.font = pygame.font.Font
        self.uncompleted = list
        self.completed = str

    def exec(self):
        from Globals.Variables import game_state, levels, rules
        self.uncompleted = list()
        self.font = pygame.font.Font('../Media/Pangolin-Regular.ttf', 25)
        for level in levels:
            if not level.completed:
                self.uncompleted.append([level, []])
                for memorial in level.memorials:
                    if not memorial.completed:
                        self.uncompleted[-1][-1].append(memorial)

        if not self.uncompleted:
            self.completed = 'Поздравляем, игра пройдена!'
        else:
            self.completed = 'Игра пройдена не полностью.'

        self.screen = pygame.display.set_mode((1280, 720))
        rules.append(self.render())

    def render(self):
        self.screen.fill((255, 255, 255))
        y_offset = 40

        for line in split_text_into_lines(self.completed, self.font, self.screen.get_width()):
            text_surface = self.font.render(line, True, (0, 0, 0))
            text_rect = text_surface.get_rect(centerx=self.screen.get_rect().centerx, y=y_offset)
            self.screen.blit(text_surface, text_rect)
            y_offset += text_rect.height + 5

        for level, memorials in self.uncompleted:
            txt = f"{level.name}: {', '.join(m.name for m in memorials)}" if memorials else None
            if not txt:
                continue

            for line in split_text_into_lines(txt, self.font, self.screen.get_width() - 80):
                text_surface = self.font.render(line, True, (0, 0, 0))
                self.screen.blit(text_surface, (40, y_offset))
                y_offset += text_surface.get_rect().height + 5