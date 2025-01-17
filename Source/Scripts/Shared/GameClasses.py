from CarsMiniGame.CarsMiniGame import CarsMiniGame
from CityScreen.CityScreen import CityScreen
from LoadMenu.LoadMenu import LoadMenu
from MainMenu.MainMenu import MainMenu
from MemorialScreen.MemorialScreen import MemorialScreen
from MemorialScreen.Selector import Selector
from PuzzleMiniGame.PuzzleMiniGame import PuzzleMiniGame


class GameClasses:
    def __init__(self):
        self.LoadMenu = LoadMenu()
        self.MainMenu = MainMenu()
        self.MemorialScreen = MemorialScreen()
        self.Selector = Selector()
        self.CityScreen = CityScreen()
        self.CarsMiniGame = CarsMiniGame()
        self.PuzzleMiniGame = PuzzleMiniGame()