from pathlib import Path

import pygame


class Media:
    def __init__(self, pygame_instance):
        self.mixer = pygame_instance.mixer
        self.mixer.init()

        # звуки
        self.sound_hp_lost = pygame_instance.mixer.Sound(Path("sounds_game/hit_sound.wav"))
        self.sound_heal = pygame_instance.mixer.Sound(Path("sounds_game/heal_sound.wav"))
        self.sound_power_up = pygame_instance.mixer.Sound(Path("sounds_game/power_up_sound.wav"))
        self.sound_reload = pygame_instance.mixer.Sound(Path("sounds_game/reload.wav"))
        self.sound_coin = pygame_instance.mixer.Sound(Path("sounds_game/coin_sound.wav"))
        self.sound_mob_kill = pygame_instance.mixer.Sound(Path("sounds_game/mob_kill_sound.wav"))
        self.sound_game_over = pygame_instance.mixer.Sound(Path("sounds_game/death.wav"))
        self.sound_explosion = pygame_instance.mixer.Sound(Path("sounds_game/explosion.wav"))
        self.sound_shot = pygame_instance.mixer.Sound(Path("sounds_game/laser_sound.wav"))


        # фоновая музыка
        self.music_menu = Path("sounds_game/main_menu_music.mp3")
        self.music_game = Path("sounds_game/ambient_music.mp3")

        # устанавливаем громкость звуков
        self.sound_hp_lost.set_volume(2)
        self.sound_shot.set_volume(0.3)
        self.sound_coin.set_volume(0.1)

        # шрифты
        self.font_menu = pygame_instance.font.Font(Path('data_game/kenvector_future.ttf'), 60)
        self.font_menu_info = pygame_instance.font.Font(Path('data_game/kenvector_future.ttf'), 30)
        self.font_game_pause = pygame_instance.font.Font(Path('data_game/kenvector_future.ttf'), 20)
        self.font_game_over = pygame_instance.font.Font(Path('data_game/kenvector_future.ttf'), 70)
        self.font_menu_color = 'black'

        # скины кнопок
        self.menu_button_background = "buttonRed.png"
        self.menu_button_background_mouse_over = "buttonYellow.png"
        self.button_pause = "pause_menu.png"
        self.game_over_menu_button = "button_menu_not_pressed.png"
        self.game_over_menu_button_mouse_over = "button_menu_pressed.png"
        self.game_over_retry_button = "button_restart_not_pressed.png"
        self.game_over_retry_button_mouse_over = "button_restart_pressed.png"
