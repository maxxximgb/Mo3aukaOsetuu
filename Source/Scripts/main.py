import sys
import pygame
from LoadMenu.LoadMenu import LoadMenu
from Globals.Globals import rules, events

pygame.init()
pygame.mixer.init()
running = True
menu = LoadMenu()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for e in events:
            if callable(e):
                e(event) # Вызов ивентов

    for rule in rules:  # Вызов правил окон (отображение картинки итд.) Чтобы добавить правило, нужно в список rules добавить необходимую функцию НЕ ВЫЗВАННУЮ.
        if callable(rule):
            rule()

    pygame.display.flip()

pygame.quit()