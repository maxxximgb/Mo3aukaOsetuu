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
        self.preview = None
        self.images = []
        self.name = ''
        self.desc = ''
        self.puzzleparts = []
        self.puzzlepos = []