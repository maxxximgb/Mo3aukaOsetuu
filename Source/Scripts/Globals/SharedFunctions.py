import pygame

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

