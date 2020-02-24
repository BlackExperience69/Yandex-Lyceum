import random
import pygame
from os import path

pygame.init()
pygame.mixer.init()
img_dir = path.join(path.dirname(__file__), 'images')
score = 0

def load_image_convert_alpha(filename):
    """Словарь с картинками..."""
    return pygame.image.load(os.path.join('images', filename)).convert_alpha()


def load_sound(filename):
    """Словарь со звуком"""
    return pygame.mixer.Sound(os.path.join('sounds', filename))
