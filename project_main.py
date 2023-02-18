import os
import random
import sys
from pathlib import Path

import pygame

import media

file = open("resourses.txt")

if file:
    lines = file.readlines()
    all_coins = int(lines[0].split()[0])
    high_score = int(lines[1].split()[0])
    all_games = int(lines[2].split()[0])
file.close()

# Размеры
WIDTH = 600
HEIGHT = 600
OUT_OF_SCREEN = -WIDTH
FPS = 60

# жизни и всё с нимим связанное
START_HEALTH = 3
health = START_HEALTH

# доп параметры
can_view = 30
reload = 30
coins = 0
min_meteors = 7
weapon_level = 0

# проигрыш
game_over = False

# Создаем игру и окно
pygame.init()
media = media.Media(pygame)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space battle")
clock = pygame.time.Clock()


# Загрузчик картинок
def load_image(name, colorkey=None):
    fullname = os.path.join('data_game', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()

    return image


# родительский класс
class GameObject(pygame.sprite.Sprite):
    colorkey = None

    def __init__(self, image_path, pos_x, pos_y, size_x=None, size_y=None):
        pygame.sprite.Sprite.__init__(self)
        self.set_image(image_path, size_x, size_y)
        self.set_position(pos_x, pos_y)

    def set_position(self, pos_x, pos_y):
        self.rect.x = pos_x
        self.rect.y = pos_y

    def set_image(self, image_path, size_x=None, size_y=None):
        self.image = load_image(image_path, self.colorkey)
        if size_x is not None and size_y is not None:
            self.image = pygame.transform.scale(self.image, (size_x, size_y))
        self.rect = self.image.get_rect()


# объект с изменяемой позицией
class GameObjectUpdatable(GameObject):
    def update(self):
        super().update()
        pass


class hp(GameObject):
    def __init__(self, pos_x):
        super().__init__("heart.png", pos_x, 30, 30, 30)


# Класс Игрока
class Player(GameObjectUpdatable):

    def __init__(self):
        super().__init__("playerShip1_orange.png", WIDTH / 2, HEIGHT - 10)
        self.mask = pygame.mask.from_surface(self.image)

        self.shot = False
        self.reload = 0
        self.reload_full = reload

        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.speedy = 0
        self.shot = 0

    def update_reload(self, new_reload):
        self.reload_full = new_reload

    def update(self):
        super().update()

        self.speedx = 0
        self.speedy = 0
        self.mask = pygame.mask.from_surface(self.image)

        # Управление с помощью WASD
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a]:
            self.speedx = -3
        if keystate[pygame.K_d]:
            self.speedx = 3
        if keystate[pygame.K_w]:
            self.speedy = -5
        if keystate[pygame.K_s]:
            self.speedy = 5
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # Границы игрового поля
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        # Перезарядка и стрельба
        mousestate = pygame.mouse.get_pressed()
        if mousestate[0] and not self.shot:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            self.shot = True
            media.sound_shot.play()

        if self.shot and self.reload < self.reload_full:
            self.reload += 1
        else:
            self.shot = False
            self.reload = 0

        # Эффект тряски
        self.rect.x += random.randint(-1, 1)
        self.rect.y += random.randint(-1, 1)

    def damage(self):
        self.rect.x += random.randint(-5, 5)
        self.rect.y += random.randint(-5, 5)

    def get_coords(self):
        return self.rect.x, self.rect.y


# класс отрисовки щита
class Shield(GameObjectUpdatable):
    SHIELD_ACTIVE = 120
    timer = 0

    def __init__(self, owner):
        self.owner = owner
        self.dspl_x = -11
        self.dspl_y = -25
        super().__init__("shield3.png",
                         self.owner.get_coords()[0] + self.dspl_x,
                         owner.get_coords()[1] + self.dspl_y,
                         120,
                         120)

    def update(self, exec=None):
        # перемещение
        if self.is_active():
            self.rect.x = self.owner.get_coords()[0] + self.dspl_x
            self.rect.y = self.owner.get_coords()[1] + self.dspl_y
            if self.timer > 0:
                self.timer -= 1
        else:
            self.rect.x = OUT_OF_SCREEN
            self.rect.y = OUT_OF_SCREEN

    def set_active(self, time=SHIELD_ACTIVE):
        self.timer = time

    def is_active(self):
        return self.timer > 0


# Класс моба/астероида
class Mob(pygame.sprite.Sprite):
    def __init__(self, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        meteor_type_chance = random.randrange(1, 100)
        meteor_angle_chance = random.randrange(0, 360)
        if meteor_type_chance > 60:
            self.image = load_image("meteorGrey.png", colorkey=0)
            self.image = pygame.transform.scale(self.image, (size, size))
            self.image = pygame.transform.rotate(self.image, meteor_angle_chance)
        elif 40 < meteor_type_chance <= 60:
            self.image = load_image("meteorGreyside.png", colorkey=0)
            self.image = pygame.transform.scale(self.image, (size, size))
            self.image = pygame.transform.rotate(self.image, meteor_angle_chance)
        elif 20 < meteor_type_chance <= 40:
            self.image = load_image("meteorBrown.png", colorkey=0)
            self.image = pygame.transform.scale(self.image, (size, size))
            self.image = pygame.transform.rotate(self.image, meteor_angle_chance)
        elif 0 < meteor_type_chance <= 20:
            self.image = load_image("meteorBrownside.png", colorkey=0)
            self.image = pygame.transform.scale(self.image, (size, size))
            self.image = pygame.transform.rotate(self.image, meteor_angle_chance)

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(3, 8)
        self.speedx = random.randrange(-3, 3)

        self.delay1, self.delay2 = None, None

    def update(self, exec=None):
        # Скорость
        mob_kill_sound = pygame.mixer.Sound(Path("sounds_game/mob_kill_sound.wav"))
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 8)

        # Смерть со спрайтом взрыва(+ задержка в три кадра)
        if self.delay2:
            mob_kill_sound.play()
            self.make_heal()
            self.make_power_up()
            self.make_coin()
            self.make_shield()
            self.kill()
        if self.delay1:
            self.delay2 = True
        if exec:
            self.image = load_image("booom.png", colorkey=-1)
            self.image = pygame.transform.scale(self.image, (self.size + 40, self.size + 40))
            self.delay1 = True

    def make_heal(self):
        heal_chance = random.randrange(1, 100)
        if heal_chance <= 7:
            generate_serdechka = heal(self.rect.x, self.rect.y)
            all_sprites.add(generate_serdechka)
            healki.add(generate_serdechka)

    def make_power_up(self):
        power_up_chance = random.randrange(1, 100)
        if power_up_chance <= 5 and reload > 5:
            generate_power_up = power_up(self.rect.x, self.rect.y)
            all_sprites.add(generate_power_up)
            power_ups.add(generate_power_up)

    def make_coin(self):
        coin_chance = random.randrange(1, 100)
        if coin_chance <= 10:
            generate_coin = coin(self.rect.x, self.rect.y)
            all_sprites.add(generate_coin)
            coins_group.add(generate_coin)

    def make_shield(self):
        shield_chance = random.randrange(1, 100)
        if shield_chance <= 3:
            generate_shield = shield_icon(self.rect.x, self.rect.y)
            all_sprites.add(generate_shield)
            shield_group.add(generate_shield)


class shield_icon(pygame.sprite.Sprite):
    image = load_image("powerupBlue_shield.png")
    image = pygame.transform.scale(image, (50, 50))

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = x
        self.rect.y = y

        self.speedy = random.randrange(3, 8)
        self.speedx = random.randrange(-2, 2)

    def update(self, exec=None):
        # Скорость

        self.rect.x += self.speedx
        self.rect.y += self.speedy


class coin(pygame.sprite.Sprite):
    image = load_image("coin.png", colorkey=-1)
    image = pygame.transform.scale(image, (50, 50))

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = x
        self.rect.y = y

        self.speedy = random.randrange(3, 8)
        self.speedx = random.randrange(-2, 2)

    def update(self, exec=None):
        # Скорость
        self.rect.x += self.speedx
        self.rect.y += self.speedy


class power_up(pygame.sprite.Sprite):
    image = load_image("powerupBlue_fast_reload.png", colorkey=-1)
    image = pygame.transform.scale(image, (50, 50))

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = x
        self.rect.y = y

        self.speedy = random.randrange(3, 8)
        self.speedx = random.randrange(-2, 2)

    def update(self, exec=None):
        # Скорость

        self.rect.x += self.speedx
        self.rect.y += self.speedy


class heal(pygame.sprite.Sprite):
    image = load_image("heart.png")
    image = pygame.transform.scale(image, (50, 50))

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = x
        self.rect.y = y

        self.speedy = random.randrange(3, 8)
        self.speedx = random.randrange(-2, 2)

    def update(self, exec=None):
        # Скорость

        self.rect.x += self.speedx
        self.rect.y += self.speedy


# Класс пули
class Bullet(pygame.sprite.Sprite):
    image = load_image("laserRed15.png", colorkey=-1)
    image = pygame.transform.scale(image, (10, 30))

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = Bullet.image
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        # убить, если он заходит за верхнюю часть экрана
        if self.rect.bottom < 0:
            self.kill()


# Класс фона
class Background(pygame.sprite.Sprite):
    image = load_image("darkPurple.png")
    image = pygame.transform.scale(image, (600, 600))

    def __init__(self, number):
        pygame.sprite.Sprite.__init__(self)
        self.image = Background.image
        self.rect = self.image.get_rect()
        self.number = number

        # В программе используется два спрайта фона,
        # которые чередуются последовательно на экране
        if self.number == 'first':
            self.rect.y = -600
        elif self.number == 'second':
            self.rect.y = 0

    def update(self):
        self.rect.y += 10
        # Скорость раздельно для каждого спрайта фона
        if self.number == 'first':
            if self.rect.y >= 0:
                self.rect.y = -600
        elif self.number == 'second':
            if self.rect.y >= 600:
                self.rect.y = 0


class ProtoButton(GameObjectUpdatable):
    font = media.font_menu

    def __init__(self, pos_x, pos_y, image_name, image_mouse_over_name, title, title_pos_x=0):
        super().__init__(image_name, pos_x, pos_y)
        self.image_default = self.image
        self.image_mouse_over = load_image(image_mouse_over_name)
        self.title = title
        self.title_x = pos_x + title_pos_x
        self.title_y = pos_y + 3
        self.font = media.font_menu_info
        self.text = self.font.render(title, True, media.font_menu_color)

    def handle_mouse_position(self, pos):
        if self.is_mouse_over(pos):
            self.image = self.image_mouse_over
        else:
            self.image = self.image_default

    def is_mouse_over(self, pos):
        mouse_x, mouse_y = pos
        return self.rect.collidepoint(mouse_x, mouse_y)

    def press_if_mouse_over(self, pos):
        return self.is_mouse_over(pos)

    def update_title(self, surface):
        surface.blit(self.text, (self.title_x, self.title_y))


class ButtonStart(ProtoButton):
    def __init__(self):
        super().__init__(190, 250, media.menu_button_background, media.menu_button_background_mouse_over, "start", 53)


class ButtonAuthors(ProtoButton):
    def __init__(self):
        super().__init__(190, 350, media.menu_button_background, media.menu_button_background_mouse_over, "authors", 27)

    def press_if_mouse_over(self, pos):
        if self.is_mouse_over(pos):
            show_image("authors_menu.png")


class ButtonExit(ProtoButton):

    def __init__(self):
        super().__init__(190, 400, media.menu_button_background, media.menu_button_background_mouse_over, "exit", 75)

    def press_if_mouse_over(self, pos):
        if self.is_mouse_over(pos):
            exit()


class ButtonControls(ProtoButton):

    def __init__(self):
        super().__init__(190, 300, media.menu_button_background, media.menu_button_background_mouse_over, "controls",
                         12)

    def press_if_mouse_over(self, pos):
        if self.is_mouse_over(pos):
            show_image("controls_menu.png")


# кнопки в конце игры
class ButtonReturnMenu(ProtoButton):

    def __init__(self):
        super().__init__(50, 400, media.game_over_menu_button, media.game_over_menu_button_mouse_over, "return", 25)

    def press_if_mouse_over(self, pos):
        return self.is_mouse_over(pos)


# class ButtonRestart
class ButtonRestart(ProtoButton):

    def __init__(self):
        super().__init__(450, 410, media.game_over_retry_button, media.game_over_retry_button_mouse_over, "restart", 25)

    def press_if_mouse_over(self, pos):
        return self.is_mouse_over(pos)


def main_menu():
    global all_games
    global all_coins
    global high_score
    global reload
    global min_meteors
    running_menu = True
    all_coins += coins
    if total_hits > high_score:
        high_score = total_hits
    start_sprite = pygame.sprite.Group()
    sprite = pygame.sprite.Sprite()
    sprite.image = load_image("start.png")
    start_sprite.add(sprite)
    sprite.rect = sprite.image.get_rect()
    background_sprites = pygame.sprite.Group(Background('first'), Background('second'))

    button_group = pygame.sprite.Group(ButtonStart(), ButtonAuthors(), ButtonControls(), ButtonExit())

    # Фоновая музыка
    pygame.mixer.music.load(media.music_menu)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    # цикл запуска меню
    while running_menu:
        for menu_event in pygame.event.get():
            if menu_event.type == pygame.QUIT:
                exit()
            if menu_event.type == pygame.MOUSEMOTION:
                button_group.update()
                for i in button_group:
                    i.handle_mouse_position(menu_event.pos)

            if menu_event.type == pygame.MOUSEBUTTONDOWN:
                for i in button_group:
                    if i.press_if_mouse_over(menu_event.pos):
                        if i.title == "start":
                            shield.set_active()
                            running_menu = False
                            init_health()
                            reload = 30
                            player.update_reload(reload)
                            min_meteors = 7
                            media.mixer.music.load(media.music_game)
                            pygame.mixer.music.play()

        background_sprites.update()
        background_sprites.draw(screen)
        start_sprite.draw(screen)
        button_group.update()
        button_group.draw(screen)

        for i in button_group:
            i.update_title(screen)

        pygame.display.flip()
        clock.tick(FPS)


def game_over_menu(points, pause_restart=False, pause_return=False):
    global health, all_coins, total_hits, coins
    global player
    global reload
    global min_meteors
    health = 3
    player.rect.centerx = WIDTH / 2
    player.rect.bottom = HEIGHT - 10
    button_group = pygame.sprite.Group(ButtonReturnMenu(), ButtonRestart())

    game_over_clock = pygame.time.Clock()
    death_sound = media.sound_game_over
    death_sound.play()
    pygame.mixer.music.stop()

    all_game_over_sprites = pygame.sprite.Group()
    game_over_sprite = pygame.sprite.Sprite()
    game_over_sprite.image = load_image("game_over.png")
    game_over_sprite.rect = game_over_sprite.image.get_rect()
    all_game_over_sprites.add(game_over_sprite)

    all_coins += coins
    file = open('resourses.txt', 'w+', encoding='utf-8')
    file.seek(0)
    file.write(str(all_coins) + ' coins')
    if total_hits > high_score:
        file.write('\n' + str(total_hits) + ' high score')
    else:
        file.write('\n' + str(high_score) + ' high score')
    file.write('\n' + str(all_games) + ' games_played')
    file.close()

    game_over_running = True
    game_over_sprite.rect.x = 0
    game_over_sprite.rect.y = -600

    if pause_return:
        total_hits, coins = 0, 0
        game_over_running = False
        reload = 30
        player.update_reload(reload)
        min_meteors = 7
        main_menu()
    elif pause_restart:
        total_hits, coins = 0, 0
        init_health()
        reload = 30
        player.update_reload(reload)
        min_meteors = 7
        media.mixer.music.load(media.music_game)
        pygame.mixer.music.play()
        game_over_running = False

    while game_over_running:
        all_game_over_sprites.update()
        all_game_over_sprites.draw(screen)
        button_group.draw(screen)

        font = media.font_game_over
        text = font.render(points, True, 'white')
        screen.blit(text, (460, 148))

        if 0 < int(points) > high_score:
            font = media.font_menu_info
            text = font.render("NEW BEST SCORE!", True, 'white')
            screen.blit(text, (140, 220))

        font = media.font_menu_info
        text = font.render('Coins picked up: ' + str(coins), True, 'white')
        screen.blit(text, (130, 550))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_over_running = False
            if event.type == pygame.MOUSEMOTION:
                button_group.update()
                for i in button_group:
                    i.handle_mouse_position(event.pos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                for i in button_group:
                    if i.press_if_mouse_over(event.pos):
                        if i.title == "return":
                            coins = 0
                            game_over_running = False
                            reload = 30
                            player.update_reload(reload)
                            min_meteors = 7
                            main_menu()
                        elif i.title == "restart":
                            coins = 0
                            init_health()
                            reload = 30
                            player.update_reload(reload)
                            min_meteors = 7
                            media.mixer.music.load(media.music_game)
                            pygame.mixer.music.play()
                            game_over_running = False

        if game_over_sprite.rect.y < 0:
            game_over_sprite.rect.y += 100
        else:
            game_over_sprite.rect.y = 0
        button_group.update()
        clock.tick(FPS)
        pygame.display.flip()


class Button_background(pygame.sprite.Sprite):
    def __init__(self, image_name):
        pygame.sprite.Sprite.__init__(self)

        Button_background.image = load_image(image_name)
        Button_background.image = pygame.transform.scale(Button_background.image, (600, 600))

        self.image_name = image_name
        self.image_background = Button_background.image
        self.rect = self.image.get_rect()


def show_image(image_name):
    background_sprite = pygame.sprite.Group(Button_background(image_name))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        background_sprite.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)


class Pause_background(pygame.sprite.Sprite):
    image = load_image(media.button_pause)
    image = pygame.transform.scale(image, (WIDTH, HEIGHT))

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = Pause_background.image
        self.rect = self.image.get_rect()


def game_pause(sprites, points):
    global min_meteors
    background_sprite = pygame.sprite.Group(Pause_background())
    button_group = pygame.sprite.Group(ButtonReturnMenu(), ButtonRestart())

    running = True
    while running:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEMOTION:
                button_group.update()
                for i in button_group:
                    i.handle_mouse_position(event.pos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                for i in button_group:
                    if i.press_if_mouse_over(event.pos):
                        if i.title == "return":
                            game_over_menu('0', pause_return=True)
                            running = False
                        elif i.title == "restart":
                            game_over_menu('0', pause_restart=True)
                            running = False

        sprites.draw(screen)
        background_sprite.draw(screen)
        button_group.update()
        button_group.draw(screen)

        font = pygame.font.Font('data_game/kenvector_future.ttf', 40)
        text = font.render(f"Score: {str(points)}", True, 'white')
        screen.blit(text, (180, 200))

        font3 = pygame.font.Font('data_game/kenvector_future.ttf', 40)
        text3 = font3.render('Coins picked up: ' + str(coins), True, 'white')
        screen.blit(text3, (70, 250))

        font = pygame.font.Font('data_game/kenvector_future.ttf', 40)
        text = font.render("Best score: " + str(high_score), True, 'white')
        screen.blit(text, (90, 300))

        font = media.font_game_pause
        text = font.render('after restarting', True, 'white')
        screen.blit(text, (175, 530))
        text = font.render('your progress will not be saved', True, 'white')
        screen.blit(text, (75, 550))

        clock.tick(FPS)


total_hits = 0

# паузы
pause = 0
health_pause = 0
power_up_pause = 0
coin_pause = 0

all_sprites = pygame.sprite.Group()
power_ups = pygame.sprite.Group()
mobs = pygame.sprite.Group()

healki = pygame.sprite.Group()
health_sprite_group = pygame.sprite.Group()
bullets = pygame.sprite.Group()
shield_group = pygame.sprite.Group()
information_icons = pygame.sprite.Group()
player = Player()
shield = Shield(player)
coins_group = pygame.sprite.Group()
background1, background2 = Background('first'), Background('second')
all_sprites.add(background1, background2, player, shield)
for i in range(8):
    m = Mob(random.randrange(50, 90))
    all_sprites.add(m)
    mobs.add(m)


def init_health():
    global health_sprite_group
    health_sprite_group = pygame.sprite.Group()
    d = 0
    for j in range(health):
        h = hp(d)
        health_sprite_group.add(h)
        d += 30


# Цикл игры
shooting = False
running = True
main_menu()

# фоновая музыка
media.mixer.music.load(media.music_game)
media.mixer.music.set_volume(0.3)
media.mixer.music.play(-1)

init_health()

while running:

    asteroids_count = str(mobs)
    if int(asteroids_count[7:9]) < min_meteors:
        m = Mob(random.randrange(50, 90))
        all_sprites.add(m)
        mobs.add(m)

    healki.draw(screen)
    power_ups.draw(screen)
    coins_group.draw(screen)
    information_icons.draw(screen)
    clock.tick(FPS)

    # различные паузы
    if health_pause > 0:
        health_pause -= 1
    if power_up_pause > 0:
        power_up_pause -= 1
    if coin_pause > 0:
        coin_pause -= 1
    else:
        shild_active = False

    if pause > 0:
        pause -= 1
        if pause > 60:
            player.damage()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_pause(all_sprites, total_hits)

    # Обновление
    all_sprites.update()

    # Проверка на столкновения моба с пулей
    hits = pygame.sprite.groupcollide(mobs, bullets, False, True)
    for hit in hits:
        hit.update(True)
        m = Mob(random.randrange(30, 70))
        all_sprites.add(m)
        mobs.add(m)
        total_hits += 1

    # Проверка, не ударил ли моб игрока
    hits = pygame.sprite.spritecollide(player, mobs, False)
    if hits:
        pass
    if hits and not shield.is_active():
        health -= 1
        media.sound_hp_lost.play()
        shield.set_active()
        hits = False
        init_health()
        blocks_hit_list = pygame.sprite.spritecollide(player, mobs, True)
        if health == 0:
            media.mixer.Sound(media.sound_explosion).play()
            pygame.mixer.music.stop()
            game_over_menu(str(total_hits))
            total_hits = 0

    # Проверка, столкновения игрока и сердца
    hits = pygame.sprite.spritecollide(player, healki, False)
    if hits and health < 3 and health_pause <= 0:
        health_pause = 30
        health += 1
        media.sound_heal.play()
        init_health()
        blocks_hit_list = pygame.sprite.spritecollide(player, healki, True)

    # Проверка, столкновения игрока и ускорения перезорядки
    hits = pygame.sprite.spritecollide(player, power_ups, False)
    if hits and power_up_pause <= 0:
        power_up_pause = 30
        media.sound_reload.play()
        weapon_level += 1
        if weapon_level % 2 != 0:
            min_meteors += 1
        if reload > 5:
            reload -= 5
        player.update_reload(reload)
        blocks_hit_list = pygame.sprite.spritecollide(player, power_ups, True)

    # Проверка, столкновения игрока и усиления щита
    hits = pygame.sprite.spritecollide(player, shield_group, False)
    if hits:
        shield.set_active()
        hits = False
        media.sound_power_up.play()
        blocks_hit_list = pygame.sprite.spritecollide(player, shield_group, True)

    # Проверка, столкновения игрока и монетки
    hits = pygame.sprite.spritecollide(player, coins_group, False)
    if hits and coin_pause <= 0:
        coin_pause = 10
        media.sound_coin.play()
        coins += 1
        blocks_hit_list = pygame.sprite.spritecollide(player, coins_group, True)

    # Проверка, столкновения щита и астеройда
    if shield.is_active():
        hits = pygame.sprite.spritecollide(shield, mobs, False)
        if hits:
            for hit in hits:
                hit.update(True)
                m = Mob(random.randrange(30, 70))
                all_sprites.add(m)
                mobs.add(m)
                total_hits += 1

            media.sound_mob_kill.play()
            blocks_hit_list = pygame.sprite.spritecollide(shield, mobs, True)

    if running:
        # Рендеринг
        screen.fill('black')
        all_sprites.draw(screen)
        health_sprite_group.draw(screen)

        # Счеты
        font = media.font_menu_info
        text = font.render('Score: ' + str(total_hits), True, 'white')
        screen.blit(text, (0, 0))
        pygame.display.flip()
