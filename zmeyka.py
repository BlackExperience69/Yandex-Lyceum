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


def draw_centered(surface1, surface2, position):
    """Прорисовка поля для игры"""
    rect = surface1.get_rect()
    rect = rect.move(position[0] - rect.width // 2, position[1] - rect.height // 2)
    surface2.blit(surface1, rect)


def rotate_center(image, rect, angle):
    """Поворот кораблика вокруг своей оси"""
    rotate_image = pygame.transform.rotate(image, angle)
    rotate_rect = rotate_image.get_rect(center=rect.center)
    return rotate_image, rotate_rect


def distance(p, q):
    """Рассчет растояния между 2 точками(кораблик и метеор, метеор и пулька)"""
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


class GameObject(object):
    """Класс для создаия и генерации объектов"""

    def __init__(self, position, image, speed=0):
        self.image = image
        self.position = list(position[:])
        self.speed = speed

    def draw_on(self, screen):
        draw_centered(self.image, screen, self.position)

    def size(self):
        return max(self.image.get_height(), self.image.get_width())

    def radius(self):
        return self.image.get_width() / 2


class Spaceship(GameObject):
    def __init__(self, position):
        """Инициализация объекта космического корабля с учетом его положения"""
        super(Spaceship, self).__init__(position, load_image_convert_alpha('zaca.png'))

        self.image_on = load_image_convert_alpha('zacaf.png')
        self.image_die = load_image_convert_alpha('bang.png')
        self.direction = [0, -1]
        self.is_throttle_on = False
        self.bang = False
        self.angle = 0

        # список для хранения ракет, выпущенных кораблем
        self.active_missiles = []

    def draw_on(self, screen):
        """Прорисовка корыбля"""

        # Находится ли корабль в движении или нет
        if self.bang:
            new_image, rect = rotate_center(self.image_die, self.image_on.get_rect(), self.angle)

        if self.is_throttle_on:
            new_image, rect = rotate_center(self.image_on, self.image_on.get_rect(), self.angle)

        else:
            new_image, rect = rotate_center(self.image, self.image.get_rect(), self.angle)

        draw_centered(new_image, screen, self.position)

    def move(self):
        """Стоит ли обновлять один кадр для объекта..."""

        # calculate the direction from the angle variable
        self.direction[0] = math.sin(-math.radians(self.angle))
        self.direction[1] = -math.cos(math.radians(self.angle))

        # calculate the position from the direction and speed
        self.position[0] += self.direction[0] * self.speed
        self.position[1] += self.direction[1] * self.speed

    def fire(self):
        """Создание пули и выстрел"""

        # корректировка ракеты по углу наклона космического корабля
        # adjust [] используется для удержания положения точки откуда должна быть выпущена ракета
        adjust = [0, 0]
        adjust[0] = math.sin(-math.radians(self.angle)) * self.image.get_width()
        adjust[1] = -math.cos(math.radians(self.angle)) * self.image.get_height()

        # Создание новой ракеты
        new_missile = Missile((self.position[0] + adjust[0], self.position[1] + adjust[1] / 2), self.angle)
        self.active_missiles.append(new_missile)


class Missile(GameObject):
    """Создание ракеты"""

    def __init__(self, position, angle, speed=15):
        super(Missile, self).__init__(position, load_image_convert_alpha('missile.png'))

        self.angle = angle
        self.direction = [0, 0]
        self.speed = speed

    def move(self):
        """Движение ракеты"""

        # Вычисление направления по переменной угла(так проще)
        self.direction[0] = math.sin(-math.radians(self.angle))
        self.direction[1] = -math.cos(math.radians(self.angle))

        # Вычисление позиции согласно направлению и скорости
        self.position[0] += self.direction[0] * self.speed
        self.position[1] += self.direction[1] * self.speed


class Rock(GameObject):
    """Метеориты"""

    def __init__(self, position, size, speed=4):
        """Инициализация метеора: его размер и позиция"""

        # если размер допустим
        if size in {"big", "normal", "small"}:

            # загружаем изображение
            str_filename = "rock-" + str(size) + ".png"
            super(Rock, self).__init__(position, load_image_convert_alpha(str_filename))
            self.size = size

        self.position = list(position)

        self.speed = speed

        # Создание рандомного направления
        if bool(random.getrandbits(1)):
            rand_x = random.random() * -1
        else:
            rand_x = random.random()

        if bool(random.getrandbits(1)):
            rand_y = random.random() * -1
        else:
            rand_y = random.random()

        self.direction = [rand_x, rand_y]

    def move(self):
        """Движение метеора"""

        self.position[0] += self.direction[0] * self.speed
        self.position[1] += self.direction[1] * self.speed


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

    def run(self):
        """Бесконечный цикл обработки событий"""
        running = True
        while running:
            event = pygame.event.wait()

            # Хочу выйти
            if event.type == pygame.QUIT:
                running = False

            # Состояние игры - презапуск
            elif event.type == MyGame.REFRESH:

                if self.state != MyGame.WELCOME:

                    keys = pygame.key.get_pressed()

                    if keys[pygame.K_SPACE]:
                        new_time = datetime.datetime.now()
                        if new_time - self.fire_time > \
                                datetime.timedelta(seconds=0.15):
                            # между ними должно быть не менее 0,15 задержки
                            # запуск каждой ракеты

                            # запустить ракету
                            self.spaceship.fire()

                            # ПИУУУУУУ
                            self.missile_sound.play()

                            # Время выстрела
                            self.fire_time = new_time

                    if self.state == MyGame.PLAYING:
                        # Продолжение игры

                        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                            # при нажатии клавиши "d" или "Стрелка вправо" поворот
                            # космического корабля по часовой стрелке на 10 градусов
                            self.spaceship.angle -= 10
                            self.spaceship.angle %= 360

                        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                            # при нажатии клавиши "d" или "Стрелка вправо" поворот
                            # космического корабля против часовой стрелки на 10 градусов
                            self.spaceship.angle += 10
                            self.spaceship.angle %= 360

                        if keys[pygame.K_UP] or keys[pygame.K_w]:
                            # если нажата "w" или "стрелка вверх" ,
                            # мы должны ускориться
                            self.spaceship.is_throttle_on = True

                            # расчет скорости
                            if self.spaceship.speed < 20:
                                self.spaceship.speed += 1
                        else:
                            # если клавиша дроссельной заслонки ("d" или " up")
                            # не нажимается, притормози
                            if self.spaceship.speed > 0:
                                self.spaceship.speed -= 1
                            self.spaceship.is_throttle_on = False

                        # если на экране есть ракеты, обработайте их
                        if len(self.spaceship.active_missiles) > 0:
                            self.missiles_physics()

                        # Физика метеоров
                        if len(self.rocks) > 0:
                            self.rocks_physics()

                        # физика корабля
                        self.physics()

                # нарисовать
                self.draw()

            # Воскрешение
            elif event.type == MyGame.START:
                pygame.time.set_timer(MyGame.START, 0)  # обнуление таймера
                if self.lives < 1:
                    self.game_over()
                else:
                    self.rocks = []
                    for i in range(4):
                        self.make_rock()
                    # начать заново
                    self.start()

            # Перейти от гейм овера к игре
            elif event.type == MyGame.RESTART:
                pygame.time.set_timer(MyGame.RESTART, 0)  # turn the timer off
                self.state = MyGame.STARTING

            # пользователь нажимает, чтобы начать новую игру
            elif event.type == pygame.MOUSEBUTTONDOWN and (self.state == MyGame.STARTING or
                                                           self.state == MyGame.WELCOME):
                self.do_init()

            # Press Enter
            elif event.type == pygame.KEYDOWN \
                    and event.key == pygame.K_RETURN and (self.state == MyGame.STARTING or
                                                          self.state == MyGame.WELCOME):
                self.do_init()

    def game_over(self):
        """Смерть"""
        self.soundtrack.stop()
        self.state = MyGame.GAME_OVER

        self.gameover_sound.play()
        delay = int((self.gameover_sound.get_length() + 1) * 1000)
        pygame.time.set_timer(MyGame.RESTART, delay)


    def die(self):
        """Потеря жизни"""
        self.soundtrack.stop()
        # Не начать пока не закончится смерть
        self.lives -= 1
        self.counter = 0
        self.state = MyGame.DYING

        self.die_sound.play()
        delay = int((self.die_sound.get_length() + 1) * 1000)
        pygame.time.set_timer(MyGame.START, delay)

    def physics(self):
        """Физика жизни"""

        if self.state == MyGame.PLAYING:
            # вызрв функции движения
            self.spaceship.move()

            """План осуществить анти-выход за границы"""

    def missiles_physics(self):
        """Физика пулек"""

        # Активные пульки
        if len(self.spaceship.active_missiles) > 0:
            for missile in self.spaceship.active_missiles:
                # Их движение
                missile.move()

                # проверьте столкновение с каждым камнем
                for rock in self.rocks:
                    if rock.size == "big":
                        # если ракета попадет в Большой Камень, уничтожьте его,
                        # сделайте два камня среднего размера и дайте 20 баллов
                        if distance(missile.position, rock.position) < 80:
                            self.rocks.remove(rock)
                            if missile in self.spaceship.active_missiles:
                                self.spaceship.active_missiles.remove(missile)
                            self.make_rock("normal", (rock.position[0] + 10, rock.position[1]))
                            self.make_rock("normal", (rock.position[0] - 10, rock.position[1]))
                            self.score += 20

                    elif rock.size == "normal":
                        # если ракета попадет в камень среднего размера, уничтожьте его,
                        # сделайте два небольших камня и дайте 50 баллов
                        if distance(missile.position, rock.position) < 55:
                            self.rocks.remove(rock)
                            if missile in self.spaceship.active_missiles:
                                self.spaceship.active_missiles.remove(missile)
                            self.make_rock("small", (rock.position[0] + 10, rock.position[1]))
                            self.make_rock("small", (rock.position[0] - 10, rock.position[1]))
                            self.score += 50
                    else:
                        # если ракета попадет в небольшой камень, уничтожьте его,
                        # сделайте один большой камень, если есть менее 10 камней
                        # на экране, и дать 100 баллов
                        if distance(missile.position, rock.position) < 30:
                            self.rocks.remove(rock)
                            if missile in self.spaceship.active_missiles:
                                self.spaceship.active_missiles.remove(missile)

                            if len(self.rocks) < 10:
                                self.make_rock()

                            self.score += 100

    def rocks_physics(self):
        """Физика камня"""

        # Проверка камней
        if len(self.rocks) > 0:

            for rock in self.rocks:
                # Движение камня
                rock.move()

                # смерть от метеора
                if distance(rock.position, self.spaceship.position) < self.death_distances[rock.size]:
                    self.die()

                # если камень выходит из экрана, и их меньше, чем 10
                # создайте новый камень с тем же размером
                elif distance(rock.position, (self.width / 2, self.height / 2)) > \
                        math.sqrt((self.width / 2) ** 2 + (self.height / 2) ** 2):

                    self.rocks.remove(rock)
                    if len(self.rocks) < 10:
                        self.make_rock(rock.size)

    def draw(self):
        """Обновление дисплея"""
        # все, что мы рисуем сейчас, находится в буфере, который не отображается
        self.screen.blit(self.bg_color, (0, 0))

        # если нас нет на экране приветствия
        if self.state != MyGame.WELCOME:

            # Рисуем кораблик
            self.spaceship.draw_on(self.screen)

            # При отсутствии актив-пулек
            if len(self.spaceship.active_missiles) > 0:
                for missile in self.spaceship.active_missiles:
                    missile.draw_on(self.screen)

            # Метеоры... Снова они
            if len(self.rocks) > 0:
                for rock in self.rocks:
                    rock.draw_on(self.screen)

            # При состоянии игры - играет
            if self.state == MyGame.PLAYING:

                # Счетчик += 1
                self.counter += 1

                if self.counter == 20 * self.FPS:

                    # Повышение сложности(20 секунд без смерти)

                    if len(self.rocks) < 15:
                        # Новый камушек
                        self.make_rock()

                    # Минимальное расстояния для создания
                    if self.min_rock_distance < 200:
                        self.min_rock_distance -= 50

                    # Обнуление Счетчика

            # дисплэй Счетчика
            scores_text = self.medium_font.render(str(self.score), True, (0, 155, 0))
            draw_centered(scores_text, self.screen,
                          (self.width - scores_text.get_width(), scores_text.get_height() + 10))

            # если игра окончена, выведите текст игры на экран
            if self.state == MyGame.GAME_OVER or self.state == MyGame.STARTING:
                draw_centered(self.gameover_text, self.screen, (self.width // 2, self.height // 2 -
                                                                self.gameover_text.get_height()))

                draw_centered(self.gameover1_text, self.screen, (self.width // 2, self.height // 2 +
                                                                 self.gameover_text.get_height()))

            # Дисплей жизни
            for i in range(self.lives):
                draw_centered(self.lives_image, self.screen, (self.lives_image.get_width() * i * 1.2 + 40,
                                                              self.lives_image.get_height() // 2))

        else:
            # Приветствие
            draw_centered(self.welcome_asteroids, self.screen, (self.width // 2, self.height // 2 -
                                                                self.welcome_asteroids.get_height()))

            draw_centered(self.welcome_desc, self.screen, (self.width // 2, self.height // 2 +
                                                           self.welcome_desc.get_height()))

        pygame.display.flip()


MyGame().run()
pygame.quit()
sys.exit()
