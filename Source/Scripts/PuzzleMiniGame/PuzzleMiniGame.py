import os.path
import time
import pygame
import random
import copy

from Shared.SharedFunctions import switch

game_state, rules, events, screen = [None] * 4


class EmptyPart:
    def __init__(self, position):
        self.position = position
        self.puzzle_part = None


class PuzzlePart(pygame.sprite.Sprite):
    def __init__(self, image, position, correct_position):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=position)
        self.correctPos = correct_position
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.cell = None

    def update(self):
        if self.dragging:
            global screen
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.rect.x = mouse_x + self.offset_x
            self.rect.y = mouse_y + self.offset_y
            self.rect.x = max(0, min(self.rect.x, screen.get_width() - self.rect.width))
            self.rect.y = max(0, min(self.rect.y, screen.get_height() - self.rect.height))


class Cell(pygame.sprite.Sprite):
    def __init__(self, position, size):
        super().__init__()
        self.position = position
        self.size = size
        self.empty_part = EmptyPart(position)
        self.puzzle_part = None

    def set_puzzle_part(self, puzzle_part):
        if self.puzzle_part is None:
            self.puzzle_part = puzzle_part
            puzzle_part.cell = self
            self.empty_part.puzzle_part = puzzle_part

    def get_rect(self):
        cell_x = 300 + self.position[1] * self.size[0]
        cell_y = self.position[0] * self.size[1]
        return pygame.Rect(cell_x, cell_y, self.size[0], self.size[1])


class PuzzleMiniGame:
    def __init__(self):
        self.font = pygame.font.Font
        self.completed_button_rect = pygame.Rect
        self.show_image_button_rect = pygame.Rect
        self.back_button_rect = pygame.Rect
        self.solved = bool
        self.puzzle_solved = None
        self.puzzle_expire_time = time.time
        self.currentlvl = None
        self.highlight_expire_time = time.time
        self.piece_sizes = list
        self.puzzlePath = str
        self.puzzle = pygame.Surface
        self.matrix = list
        self.puzzle_pieces = list
        self.grid_size = tuple
        self.screen = pygame.Surface
        self.sprites = pygame.sprite.Group
        self.show_full_image = bool
        self.grid = list
        self.dragging_piece = None
        self.highlight_enabled = bool
        self.sound_placed = None
        self.start_time = None

    def exec(self):
        global game_state, rules, events
        from Globals.Variables import game_state, rules, events

        if self.currentlvl != id(game_state.currentobj):
            self.currentlvl = id(game_state.currentobj)
            self.solved = False
            self.highlight_expire_time = time.time()
            self.puzzle_expire_time = time.time()
            self.puzzle = game_state.currentobj.puzzle
            self.matrix = game_state.currentobj.puzzlepos
            self.puzzlePath = game_state.currentobj.puzzlePath
            self.grid_size = (0, 0)
            self.puzzle_pieces = []
            self.piece_sizes = []
            self.show_full_image = False
            self.sound_placed = pygame.mixer.Sound("../Media/puzzle.mp3")
            self.puzzle_solved = pygame.mixer.Sound("../Media/puzzlesolved.mp3")
            self.sprites = pygame.sprite.Group()
            self.highlight_enabled = False
            self.resize_puzzle()
            self.loadPieces()
            self.CreateGrid()
            self.start_time = time.time()

        self.set_screen_size()
        self.back_button_rect = pygame.Rect(50, self.puzzle.get_height() + 20, 150, 60)
        self.show_image_button_rect = pygame.Rect(250, self.puzzle.get_height() + 20, 250, 60)
        self.font = pygame.font.Font("../Media/Pangolin-Regular.ttf", 27)
        events.append(self.MouseClickEvent)
        events.append(self.KeyboardEvent)

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
        screen_height = grid_height + 100
        global screen
        screen = pygame.display.set_mode((screen_width, screen_height))
        self.screen = screen

    def loadPieces(self):
        piece_width = self.puzzle.get_width() // len(self.matrix[0])
        piece_height = self.puzzle.get_height() // len(self.matrix)
        for i, row in enumerate(self.matrix):
            self.puzzle_pieces.append([])
            for j, piece in enumerate(row):
                piece_image = pygame.image.load(os.path.join(self.puzzlePath, piece))
                piece_image = pygame.transform.scale(piece_image, (piece_width, piece_height))
                puzzle_part = PuzzlePart(
                    piece_image,
                    (random.randint(0, 300 - piece_width), random.randint(0, self.puzzle.get_height() - piece_height)),
                    (i, j),
                )
                self.puzzle_pieces[i].append(puzzle_part)
                self.sprites.add(puzzle_part)

    def CreateGrid(self):
        piece_width = self.puzzle.get_width() // len(self.matrix[0])
        piece_height = self.puzzle.get_height() // len(self.matrix)
        self.grid_size = (len(self.matrix[0]), len(self.matrix))
        self.grid = [[Cell((i, j), (piece_width, piece_height)) for j in range(self.grid_size[0])] for i in
                     range(self.grid_size[1])]
        for i, row in enumerate(self.puzzle_pieces):
            for j, piece in enumerate(row):
                self.grid[i][j].empty_part.puzzle_part = piece

    def render(self):
        if self.solved:
            self.drawPuzzleSolved()
            return
        self.screen.fill((50, 50, 50))
        pygame.draw.rect(self.screen, (100, 100, 100), (0, 0, 300, self.puzzle.get_height()))
        if self.show_full_image:
            self.screen.blit(self.puzzle, (300, 0))
        else:
            for i in range(self.grid_size[0] + 1):
                x = 300 + i * self.grid[0][0].size[0]
                pygame.draw.line(self.screen, (200, 200, 200), (x, 0), (x, self.puzzle.get_height()), 2)
            for j in range(self.grid_size[1] + 1):
                y = j * self.grid[0][0].size[1]
                pygame.draw.line(self.screen, (200, 200, 200), (300, y), (300 + self.puzzle.get_width(), y), 2)
                self.sprites.update()
                self.sprites.draw(self.screen)

        if self.dragging_piece and self.highlight_enabled:
            correct_cell = self.grid[self.dragging_piece.correctPos[0]][self.dragging_piece.correctPos[1]]
            pygame.draw.rect(self.screen, (0, 255, 0), correct_cell.get_rect(), 3)


        pygame.draw.rect(self.screen, (0, 0, 0), (0, self.puzzle.get_height(), self.screen.get_width(), 100))
        pygame.draw.rect(self.screen, (0, 128, 255), self.back_button_rect)
        back_text = self.font.render("Назад", True, (255, 255, 255))
        self.screen.blit(back_text, (self.back_button_rect.x + 30, self.back_button_rect.y + 20))

        pygame.draw.rect(self.screen, (0, 128, 255), self.show_image_button_rect)
        show_image_text = self.font.render("Показать картину", True, (255, 255, 255))
        self.screen.blit(show_image_text, (self.show_image_button_rect.x + 20, self.show_image_button_rect.y + 20))

        if time.time() < self.highlight_expire_time:
            debug_text_surface = self.font.render(f"Подсветка: {'вкл' if self.highlight_enabled else 'выкл'}", True,
                                                  (255, 255, 255))
            self.screen.blit(debug_text_surface, (self.screen.get_width() - 250, self.screen.get_height() - 40))

        if time.time() < self.puzzle_expire_time:
            debug_text_surface = self.font.render("Отладка: Сборка пазла...", True, (255, 255, 255))
            self.screen.blit(debug_text_surface, (self.screen.get_width() - 300, self.screen.get_height() - 40))

    def back_button_clicked(self):
        self.Unload()
        switch(self, game_state.gameclasses.MemorialScreen, self.screen)

    def checkPiece(self, piece):
        for row in self.grid:
            for cell in row:
                if cell.get_rect().colliderect(piece.rect):
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
                        self.is_puzzle_complete()
                        break

    def MouseClickEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.solved:
                if self.completed_button_rect.collidepoint(event.pos):
                    self.Unload()
                    switch(self, game_state.gameclasses.MemorialScreen, self.screen)
                    return
            if self.back_button_rect.collidepoint(event.pos):
                self.back_button_clicked()

            if self.show_image_button_rect.collidepoint(event.pos):
                self.show_full_image = not self.show_full_image

            for piece in reversed(self.sprites.sprites()):
                if piece.rect.collidepoint(event.pos):
                    if piece.cell is not None and piece.correctPos == piece.cell.position:
                        continue
                    piece.dragging = True
                    piece.offset_x = piece.rect.x - event.pos[0]
                    piece.offset_y = piece.rect.y - event.pos[1]
                    self.dragging_piece = piece
                    self.sprites.remove(piece)
                    self.sprites.add(piece)
                    break
        elif event.type == pygame.MOUSEBUTTONUP:
            for piece in self.sprites:
                if piece.dragging:
                    piece.dragging = False
                    self.checkPiece(piece)
                    self.dragging_piece = None

    def solvePuzzle(self):
        self.puzzle_expire_time = time.time() + 2
        for row in self.puzzle_pieces:
            for piece in row:
                correct_cell = self.grid[piece.correctPos[0]][piece.correctPos[1]]
                correct_cell.set_puzzle_part(piece)
                offset_x = (correct_cell.size[0] - piece.rect.width) // 2
                offset_y = (correct_cell.size[1] - piece.rect.height) // 2
                piece.rect.topleft = (
                    300 + correct_cell.position[1] * correct_cell.size[0] + offset_x,
                    correct_cell.position[0] * correct_cell.size[1] + offset_y
                )

        self.is_puzzle_complete()

    def KeyboardEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F9:
                self.highlight_enabled = not self.highlight_enabled
                self.highlight_expire_time = time.time() + 2
            elif event.key == pygame.K_F10:
                self.solvePuzzle()

    def is_puzzle_complete(self):
        for row in self.grid:
            for cell in row:
                if cell.puzzle_part is None or cell.puzzle_part.correctPos != cell.position:
                    return False
        self.solved = True
        self.puzzle_solved.play()
        if self.start_time is not None:
            game_state.puzzletime.append(time.time() - self.start_time)

        global screen
        screen = pygame.display.set_mode((self.puzzle.get_size()[0], self.puzzle.get_size()[1]))
        self.completed_button_rect = pygame.Rect(
            (screen.get_width() // 2) - 75,
            screen.get_height() - 80,
            150, 60
        )
        game_state.score += 150
        game_state.currentobj.completed = True

    def drawPuzzleSolved(self):
        self.screen.fill((50, 50, 50))
        self.screen.blit(self.puzzle, (0, 0))

        pygame.draw.rect(self.screen, (0, 128, 255), self.completed_button_rect)
        back_text = self.font.render("Назад", True, (255, 255, 255))
        self.screen.blit(back_text, (self.completed_button_rect.x + 25, self.completed_button_rect.y + 10))

    def Unload(self):
        if self.MouseClickEvent in events: events.remove(self.MouseClickEvent)
        if self.KeyboardEvent in events: events.remove(self.KeyboardEvent)
        if self.render in rules: rules.remove(self.render)
