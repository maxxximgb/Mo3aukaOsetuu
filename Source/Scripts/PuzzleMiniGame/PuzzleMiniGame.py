import os.path

import pygame
import random
import math

game_state, rules, events = [None] * 3

class PuzzleMiniGame:
    def __init__(self):
        self.piece_sizes = list
        self.puzzlePath = str
        self.puzzle = pygame.Surface
        self.matrix = list
        self.puzzle_pieces = list
        self.grid_size = tuple([int, int])
        self.screen = pygame.Surface
        self.sprites = pygame.sprite.Group
        self.show_full_image = bool
        self.buttons = list

    def exec(self):
        global game_state, rules, events
        from Globals.Variables import game_state, rules, events
        self.puzzle = game_state.currentobj.puzzle
        self.matrix = game_state.currentobj.puzzlepos
        self.puzzlePath = game_state.currentobj.puzzlePath
        self.puzzle_pieces = list()
        self.piece_sizes = list()
        self.buttons = list()
        self.show_full_image = False
        self.sprites = pygame.sprite.Group()
        self.screen = pygame.display.set_mode(self.puzzle.get_size())

    def loadPieces(self):
        for i, el in enumerate(self.matrix):
            self.puzzle_pieces.append(list())
            for piece in el:
                PuzzlePart(pygame.image.load(os.path.join(self.puzzlePath, piece)), (random.randint([0, 200], random.randint([10, self.puzzle.get_size()[1]]))), None)
                self.puzzle_pieces[i].append(pygame.image.load(os.path.join(self.puzzlePath, piece)))


    def CreateGrid(self):
        pass

    def toMemorial(self):
        pass

    def render(self):
        pass

    def MouseClickEvent(self, event):
        pass

class PuzzlePart(pygame.sprite.Sprite):
    def __init__(self, image, position, correct_position):
        super().__init__()
        self.image = image
        self.position = position
        self.correctPos = correct_position
