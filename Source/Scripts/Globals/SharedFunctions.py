import pygame
import time

def resize_image(image, target_width, target_height):
    original_width, original_height = image.get_size()
    original_ratio = original_width / original_height
    target_ratio = target_width / target_height

    if original_ratio > target_ratio:
        new_width = target_width
        new_height = int(target_width / original_ratio)
    else:
        new_height = target_height
        new_width = int(target_height * original_ratio)

    return pygame.transform.scale(image, (new_width, new_height))

def get_aspect_ratio(image):
    return image.get_width() / image.get_height()

def switch(current_class, new_class, screen, render_method_name="render", fade_speed=5, render_needed=True):
    from Globals.Variables import rules

    current_render_method = getattr(current_class, render_method_name, None)

    if current_render_method and current_render_method in rules:
        rules.remove(current_render_method)

    fade_surface = pygame.Surface(screen.get_size())
    fade_surface.fill((0, 0, 0))
    fade_surface.set_alpha(0)

    for alpha in range(0, 256, fade_speed):
        fade_surface.set_alpha(alpha)
        if current_render_method and render_needed:
            current_render_method()
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        time.sleep(0.01)

    if hasattr(new_class, 'exec'):
        new_class.exec()

    if fade_surface.get_size() != screen.get_size():
        fade_surface = pygame.Surface(screen.get_size())
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(0)

    new_render_method = getattr(new_class, render_method_name, None)

    if new_render_method and new_render_method in rules:
        rules.remove(new_render_method)

    for alpha in range(255, -1, -fade_speed):
        fade_surface.set_alpha(alpha)
        if new_render_method:
            new_render_method()
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        time.sleep(0.01)

    if new_render_method and new_render_method not in rules:
        rules.append(new_render_method)