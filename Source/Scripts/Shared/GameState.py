from Shared.GameClasses import GameClasses

class GameState:
    def __init__(self):
        self.score = 0
        self.currentlvl = None
        self.currentobj = None
        self.gameclasses = GameClasses()
        self.name = str
        self.car_trips = 0
        self.car_faults = 0
        self.puzzletime = []