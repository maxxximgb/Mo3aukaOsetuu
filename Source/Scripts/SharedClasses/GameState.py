from SharedClasses.GameClasses import GameClasses

class GameState:
    def __init__(self):
        self.score = 0
        self.currentlvl = None
        self.currentobj = None
        self.gameclasses = GameClasses()