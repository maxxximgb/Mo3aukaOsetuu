import pygame
from Globals.Variables import rules, events, game_state

pygame.init()
pygame.mixer.init()
running = True
game_state.gameclasses.LoadMenu.exec()

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