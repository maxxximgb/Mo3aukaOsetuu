import os.path
import pygame
import random

class EmptyPart:
    def __init__(self, position):
        self.position = position
        self.puzzle_part = None

class PuzzlePart(pygame.sprite.Sprite):
    def __init__(self, image, position, correct_position, screen):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=position)
        self.correctPos = correct_position
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.cell = None
        self.screen = screen

    def update(self):
        if self.dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.rect.x = mouse_x + self.offset_x
            self.rect.y = mouse_y + self.offset_y
            self.rect.x = max(0, min(self.rect.x, self.screen.get_width() - self.rect.width))
            self.rect.y = max(0, min(self.rect.y, self.screen.get_height() - self.rect.height))

class Cell:
    def __init__(self, position, size):
        self.position = position
        self.size = size
        self.empty_part = EmptyPart(position)
        self.puzzle_part = None

    def set_puzzle_part(self, puzzle_part):
        if self.puzzle_part is None:
            self.puzzle_part = puzzle_part
            puzzle_part.cell = self
            self.empty_part.puzzle_part = puzzle_part
        else:
            print("Ячейка уже занята!")

    def remove_puzzle_part(self):
        if self.puzzle_part is not None:
            self.puzzle_part.cell = None
            self.empty_part.puzzle_part = None
            self.puzzle_part = None
        else:
            print("Ячейка уже пуста!")

class PuzzleMiniGame:
    def __init__(self):
        self.piece_sizes = []
        self.puzzlePath = ""
        self.puzzle = None
        self.matrix = []
        self.puzzle_pieces = []
        self.grid_size = (0, 0)
        self.screen = None
        self.sprites = pygame.sprite.Group()
        self.show_full_image = False
        self.buttons = []
        self.grid = []
        self.dragging_piece = None
        self.highlight_enabled = False
        self.sound_placed = None

    def exec(self):
        global game_state, rules, events
        from Globals.Variables import game_state, rules, events

        self.puzzle = game_state.currentobj.puzzle
        self.matrix = game_state.currentobj.puzzlepos
        self.puzzlePath = game_state.currentobj.puzzlePath
        self.puzzle_pieces = []
        self.piece_sizes = []
        self.buttons = []
        self.show_full_image = False
        self.sound_placed = pygame.mixer.Sound("../Media/puzzle.mp3")
        self.sprites = pygame.sprite.Group()

        self.resize_puzzle()
        self.set_screen_size()
        self.loadPieces()
        self.CreateGrid()

        events.append(self.MouseClickEvent)
        events.append(self.KeyboardEvent)
        rules.append(self.render)

    def resize_puzzle(self):
        original_width, original_height = self.puzzle.get_size()
        min_size = 900

        if original_width >= original_height:
            new_width = min_size
            new_height = int((min_size / original_width) * original_height)
        else:
            new_height = min_size
            new_width = int((min_size / original_height) * original_width)

        self.puzzle = pygame.transform.scale(self.puzzle, (new_width, new_height))

    def set_screen_size(self):
        grid_width = self.puzzle.get_width()
        grid_height = self.puzzle.get_height()
        screen_width = grid_width + 300
        screen_height = grid_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))

    def loadPieces(self):
        piece_width = self.puzzle.get_width() // len(self.matrix[0])
        piece_height = self.puzzle.get_height() // len(self.matrix)

        for i, row in enumerate(self.matrix):
            self.puzzle_pieces.append([])
            for j, piece in enumerate(row):
                piece_image = pygame.image.load(os.path.join(self.puzzlePath, piece))
                piece_image = pygame.transform.scale(piece_image, (piece_width, piece_height))
                piece_rect = piece_image.get_rect()
                self.piece_sizes.append(piece_rect.size)
                puzzle_part = PuzzlePart(
                    piece_image,
                    (random.randint(0, 300 - piece_rect.width), random.randint(0, self.puzzle.get_height() - piece_rect.height)),
                    (i, j),
                    self.screen
                )
                self.puzzle_pieces[i].append(puzzle_part)
                self.sprites.add(puzzle_part)

    def CreateGrid(self):
        if not self.piece_sizes:
            raise ValueError("Список piece_sizes пуст. Убедитесь, что loadPieces был вызван.")

        piece_width = self.puzzle.get_width() // len(self.matrix[0])
        piece_height = self.puzzle.get_height() // len(self.matrix)

        self.grid_size = (len(self.matrix[0]), len(self.matrix))
        self.grid = []

        for i in range(self.grid_size[1]):
            row = []
            for j in range(self.grid_size[0]):
                cell = Cell((i, j), (piece_width, piece_height))
                row.append(cell)
            self.grid.append(row)

        for i, row in enumerate(self.puzzle_pieces):
            for j, piece in enumerate(row):
                self.grid[i][j].empty_part.puzzle_part = piece

    def highlight_cell(self, cell, color=(0, 255, 0), border_width=3):
        cell_x = 300 + cell.position[1] * cell.size[0]
        cell_y = cell.position[0] * cell.size[1]
        pygame.draw.rect(self.screen, color, (cell_x, cell_y, cell.size[0], cell.size[1]), border_width)

    def render(self):
        self.screen.fill((50, 50, 50))
        pygame.draw.rect(self.screen, (100, 100, 100), (0, 0, 300, self.puzzle.get_height()))

        for i in range(self.grid_size[0] + 1):
            x = 300 + i * self.grid[0][0].size[0]
            pygame.draw.line(self.screen, (200, 200, 200), (x, 0), (x, self.puzzle.get_height()), 2)
        for j in range(self.grid_size[1] + 1):
            y = j * self.grid[0][0].size[1]
            pygame.draw.line(self.screen, (200, 200, 200), (300, y), (300 + self.puzzle.get_width(), y), 2)

        if self.dragging_piece and self.highlight_enabled:
            correct_cell = self.grid[self.dragging_piece.correctPos[0]][self.dragging_piece.correctPos[1]]
            self.highlight_cell(correct_cell, color=(0, 255, 0), border_width=3)

        self.sprites.update()
        self.sprites.draw(self.screen)

        font = pygame.font.SysFont("Arial", 18)
        debug_text = font.render(f"Отладка: подсветка нужных мест {'вкл' if self.highlight_enabled else 'выкл'}", True, (255, 255, 255))
        self.screen.blit(debug_text, (10, self.screen.get_height() - 30))

        pygame.display.flip()

    def is_mouse_over_cell(self, mouse_pos, cell):
        cell_x = 300 + cell.position[1] * cell.size[0]
        cell_y = cell.position[0] * cell.size[1]
        cell_rect = pygame.Rect(cell_x, cell_y, cell.size[0], cell.size[1])
        return cell_rect.collidepoint(mouse_pos)

    def puzzleAdded(self, piece):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for row in self.grid:
            for cell in row:
                if self.is_mouse_over_cell((mouse_x, mouse_y), cell):
                    if cell.empty_part.puzzle_part == piece:
                        cell.set_puzzle_part(piece)
                        offset_x = (cell.size[0] - piece.rect.width) // 2
                        offset_y = (cell.size[1] - piece.rect.height) // 2
                        piece.rect.topleft = (
                            300 + cell.position[1] * cell.size[0] + offset_x,
                            cell.position[0] * cell.size[1] + offset_y
                        )
                        if piece.correctPos == cell.position:
                            self.sound_placed.play()
                        if self.is_puzzle_complete():
                            print("Пазл собран!")
                        break

    def MouseClickEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for piece in self.sprites:
                if piece.rect.collidepoint(event.pos):
                    if piece.cell is not None and piece.correctPos == piece.cell.position:
                        continue
                    piece.dragging = True
                    piece.offset_x = piece.rect.x - event.pos[0]
                    piece.offset_y = piece.rect.y - event.pos[1]
                    self.dragging_piece = piece
        elif event.type == pygame.MOUSEBUTTONUP:
            for piece in self.sprites:
                if piece.dragging:
                    piece.dragging = False
                    self.puzzleAdded(piece)
                    self.dragging_piece = None

    def KeyboardEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F9:
                self.highlight_enabled = not self.highlight_enabled

    def is_puzzle_complete(self):
        for row in self.grid:
            for cell in row:
                if cell.puzzle_part is None or cell.puzzle_part.correctPos != cell.position:
                    return False
        return True