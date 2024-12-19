import sys
import pygame
from MainMenu.MainMenu import MainMenu
from Globals.Globals import rules

pygame.init()
running = True
menu = MainMenu()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            sys.exit(0)

    for rule in rules:  # Вызов правил окон (отображение картинки итд.) Чтобы добавить правило, нужно в список rules добавить необходимую функцию. Пример в MainMenu
        if callable(rule):
            rule()

    pygame.display.flip()
