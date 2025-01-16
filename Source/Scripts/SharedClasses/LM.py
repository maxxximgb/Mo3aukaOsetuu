class Level:
    def __init__(self):
        self.completed = False
        self.dotpos = ()
        self.images = []
        self.name = ''
        self.desc = ''
        self.memorials = []


class Memorial:
    def __init__(self):
        self.completed = False
        self.preview = None
        self.puzzle = None
        self.images = []
        self.name = ''
        self.desc = ''
        self.puzzlePath = None
        self.puzzlepos = []