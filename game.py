from __future__ import division
import math
import sys
import os
import datetime
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


class MyGame(object):
    # определение и инициализация состояний игры
    PLAYING, DYING, GAME_OVER, STARTING, WELCOME = range(5)

    # определение особых таких состояний
    REFRESH, START, RESTART = range(pygame.USEREVENT, pygame.USEREVENT + 3)

    def __init__(self):
        """Новая игра"""

        self.counter = 0
        pygame.mixer.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()

        img_dir = path.join(path.dirname(__file__), 'images')

        # экран
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.bg_color = pygame.image.load(path.join(img_dir, 'back.jpg')).convert()

        # Загружаем музычку
        self.soundtrack = load_sound('soundtrack1.ogg')
        self.soundtrack.set_volume(.3)

        # Спецэффекты
        self.die_sound = load_sound('die1.ogg')
        self.gameover_sound = load_sound('game_over.wav')
        self.missile_sound = load_sound('fire1.ogg')

        # шрифт(размер)
        self.big_font = pygame.font.SysFont(None, 100)
        self.medium_font = pygame.font.SysFont(None, 50)
        self.small_font = pygame.font.SysFont(None, 25)

        # ПИшем
        self.gameover_text = self.big_font.render('GAME OVER!', True, (255, 0, 0))
        self.gameover1_text = self.medium_font.render('Press Enter to Restart', True, (35, 107, 142))

        # Кол-во жизней
        self.lives_image = load_image_convert_alpha('zaca.png')

        # ставим фпс
        self.FPS = 30
        pygame.time.set_timer(self.REFRESH, 1000 // self.FPS)

        # Метры до смерти от метеоров
        self.death_distances = {"big": 90, "normal": 65, "small": 40}

        # начальный экран
        self.do_welcome()

        # используется для контроля старта ракет
        # чтобы предотвратить запуск слишком большого количества ракет за короткое время
        self.fire_time = datetime.datetime.now()

    def do_welcome(self):
        """Начальный экран"""

        self.state = MyGame.WELCOME

        # Лобби
        self.welcome_asteroids = self.big_font.render("Метеоритные войны", True, (255, 215, 0))
        self.welcome_desc = self.medium_font.render("Press Enter to begin!", True, (35, 107, 142))
        self.soundtrack_menu = load_sound('menu.ogg')

        self.soundtrack_menu.set_volume(.3)


    def do_init(self):
        """Рестарт миссии"""

        # держит метеоры
        self.rocks = []

        # минимальное расстояние от космического корабля при создании камней
        # это меняется в зависимости от сложности с течением времени.
        self.min_rock_distance = 350

        # начало игры
        self.start()

        # создать метеоры(4)
        for i in range(4):
            self.make_rock()

        # Yf,jh jxrjd b rjk-dj ;bpytq
        self.lives = 3
        self.score = 0

        # счетчик, используемый для подсчета секунд
        self.counter = 0

    def make_rock(self, size="big", pos=None):
        """Создать новый метеор"""

        # Минимальное кол-во очков для создания
        margin = 200

        if pos is None:
            # Случайная позиция камешка

            rand_x = random.randint(margin, self.width - margin)
            rand_y = random.randint(margin, self.height - margin)

            # пока координата слишком близка, отбросьте ее
            # и создать еще один
            while distance((rand_x, rand_y), self.spaceship.position) < \
                    self.min_rock_distance:
                # новая координата
                rand_x = random.randint(0, self.width)
                rand_y = random.randint(0, self.height)

            temp_rock = Rock((rand_x, rand_y), size)

        else:
            # Позиция через аргумент
            temp_rock = Rock(pos, size)

        # Добавление последнего к списку
        self.rocks.append(temp_rock)

    def start(self):
        """Начало появлением героя"""
        self.spaceship = Spaceship((self.width // 2, self.height // 2))
        self.missiles = []

        # начало опенинга
        self.soundtrack.play(-1, 0, 1000)

        # Состояние игры - играет
        self.state = MyGame.PLAYING
