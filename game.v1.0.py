#Рабочий код v0.1

# =========================================================
# CYBER ROOFTOP ADVENTURE ULTIMATE
# =========================================================
# pip install pygame numpy
# =========================================================

import pygame
import random
import math
import sys
import numpy as np

pygame.init()
pygame.mixer.init()

# =========================================================
# SETTINGS
# =========================================================

WIDTH = 1280
HEIGHT = 720
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber Rooftop Adventure Ultimate")

clock = pygame.time.Clock()

# =========================================================
# AUDIO
# =========================================================

MASTER_VOLUME = 0.4

def generate_tone(freq=440, duration=0.15, volume=0.5):

    sample_rate = 44100

    n_samples = int(sample_rate * duration)

    t = np.linspace(0, duration, n_samples, False)

    wave = np.sin(freq * 2 * np.pi * t)

    audio = (wave * 32767 * volume).astype(np.int16)

    stereo = np.column_stack((audio, audio))

    return pygame.sndarray.make_sound(stereo)

jump_sound = generate_tone(700,0.12,0.4)
coin_sound = generate_tone(1200,0.08,0.5)
hurt_sound = generate_tone(220,0.2,0.5)
enemy_sound = generate_tone(500,0.15,0.5)
menu_sound = generate_tone(900,0.05,0.4)

music_notes = [
    generate_tone(220,0.3,0.15),
    generate_tone(260,0.3,0.15),
    generate_tone(330,0.3,0.15),
    generate_tone(440,0.3,0.15),
]

# =========================================================
# COLORS
# =========================================================

WHITE = (255,255,255)
BLACK = (0,0,0)

SKY = (18,24,50)

CYAN = (0,220,255)
PINK = (255,180,220)
SKIN = (255,225,190)

RED = (255,70,70)
GOLD = (255,220,0)

ROOF = (70,70,90)
ROOF_TOP = (130,180,255)

BUILDING = (15,20,45)
WINDOW = (255,220,40)

ORANGE = (255,140,0)

# =========================================================
# DAMAGE SETTINGS
# =========================================================

SPIKE_DAMAGE = 1

# =========================================================
# DIFFICULTY
# =========================================================

DIFFICULTY = {

    "EASY": {
        "enemy_speed": 2,
        "damage": 1
    },

    "NORMAL": {
        "enemy_speed": 3,
        "damage": 1
    },

    "HARD": {
        "enemy_speed": 5,
        "damage": 2
    }
}

# =========================================================
# FONTS
# =========================================================

font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 60)

# =========================================================
# STARS
# =========================================================

stars = []

for i in range(180):

    stars.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1,3)
    ])

# =========================================================
# CITY
# =========================================================

buildings = []

for i in range(0, WIDTH+300, 100):

    h = random.randint(180, 450)

    buildings.append((i,h))

# =========================================================
# PLAYER SPRITE
# =========================================================

def create_player():

    surf = pygame.Surface((96,96), pygame.SRCALPHA)

    pygame.draw.rect(surf,CYAN,(8,30,18,58),border_radius=10)
    pygame.draw.rect(surf,CYAN,(70,30,18,58),border_radius=10)

    pygame.draw.rect(surf,CYAN,(18,4,60,42),border_radius=14)

    pygame.draw.polygon(surf,PINK,[(20,10),(30,0),(38,16)])
    pygame.draw.polygon(surf,PINK,[(76,10),(66,0),(58,16)])

    pygame.draw.circle(surf,SKIN,(48,42),24)

    pygame.draw.arc(
        surf,
        BLACK,
        (30,34,14,10),
        math.pi,
        math.pi*2,
        3
    )

    pygame.draw.arc(
        surf,
        BLACK,
        (52,34,14,10),
        math.pi,
        math.pi*2,
        3
    )

    pygame.draw.arc(
        surf,
        BLACK,
        (40,48,16,10),
        0,
        math.pi,
        2
    )

    pygame.draw.circle(surf,PINK,(34,48),4)
    pygame.draw.circle(surf,PINK,(62,48),4)

    pygame.draw.rect(
        surf,
        (120,120,120),
        (34,62,28,22),
        border_radius=5
    )

    pygame.draw.polygon(
        surf,
        (0,120,255),
        [(48,62),(43,82),(53,82)]
    )

    pygame.draw.rect(surf,BLACK,(36,84,8,10))
    pygame.draw.rect(surf,BLACK,(52,84,8,10))

    return surf

# =========================================================
# ENEMY SPRITE
# =========================================================

def create_enemy():

    surf = pygame.Surface((64,64), pygame.SRCALPHA)

    pygame.draw.rect(
        surf,
        (120,220,90),
        (8,10,48,46),
        border_radius=12
    )

    pygame.draw.circle(surf,(70,180,50),(16,10),8)
    pygame.draw.circle(surf,(70,180,50),(48,10),8)

    pygame.draw.rect(
        surf,
        (240,170,120),
        (20,24,24,18),
        border_radius=4
    )

    pygame.draw.circle(surf,BLACK,(28,30),2)
    pygame.draw.circle(surf,BLACK,(36,30),2)

    pygame.draw.line(surf,BLACK,(28,38),(36,38),2)

    return surf

# =========================================================
# PLATFORM
# =========================================================

class Platform(pygame.sprite.Sprite):

    def __init__(self,x,y,w,h):

        super().__init__()

        self.image = pygame.Surface((w,h))

        self.image.fill(ROOF)

        pygame.draw.rect(
            self.image,
            ROOF_TOP,
            (0,0,w,8)
        )

        self.rect = self.image.get_rect(topleft=(x,y))

# =========================================================
# SPIKE
# =========================================================

class Spike(pygame.sprite.Sprite):

    def __init__(self,x,y):

        super().__init__()

        self.image = pygame.Surface((50,30), pygame.SRCALPHA)

        pygame.draw.polygon(
            self.image,
            (220,220,220),
            [(0,30),(12,0),(24,30)]
        )

        pygame.draw.polygon(
            self.image,
            (220,220,220),
            [(20,30),(32,0),(44,30)]
        )

        # УМЕНЬШЕННЫЙ ХИТБОКС
        self.rect = pygame.Rect(x + 8, y + 10, 30, 18)

# =========================================================
# COIN
# =========================================================

class Coin(pygame.sprite.Sprite):

    def __init__(self,x,y):

        super().__init__()

        self.image = pygame.Surface((28,28), pygame.SRCALPHA)

        pygame.draw.circle(
            self.image,
            GOLD,
            (14,14),
            12
        )

        self.rect = self.image.get_rect(topleft=(x,y))

# =========================================================
# ENEMY
# =========================================================

class Enemy(pygame.sprite.Sprite):

    def __init__(self,x,y,speed):

        super().__init__()

        self.image = create_enemy()

        self.rect = self.image.get_rect(topleft=(x,y))

        self.speed = speed

        self.start_x = x

        self.range = 150

        self.vy = 0

    def update(self,platforms):

        self.rect.x += self.speed

        if abs(self.rect.x - self.start_x) > self.range:

            self.speed *= -1

        self.vy += 1

        self.rect.y += self.vy

        hits = pygame.sprite.spritecollide(
            self,
            platforms,
            False
        )

        grounded = False

        for p in hits:

            if self.vy > 0:

                self.rect.bottom = p.rect.top

                self.vy = 0

                grounded = True

        if grounded:

            front_x = self.rect.centerx + (
                20 if self.speed > 0 else -20
            )

            front_y = self.rect.bottom + 5

            supported = False

            for p in platforms:

                if p.rect.collidepoint(front_x, front_y):

                    supported = True

            if not supported:

                self.speed *= -1

# =========================================================
# PLAYER
# =========================================================

class Player(pygame.sprite.Sprite):

    def __init__(self,x,y):

        super().__init__()

        self.base_image = create_player()
        self.image = self.base_image.copy()

        self.rect = self.image.get_rect(topleft=(x,y))

        self.vel_x = 0
        self.vy = 0

        self.acceleration = 1
        self.max_speed = 9
        self.friction = 0.85

        self.jump = -18

        self.gravity = 0.9

        self.on_ground = False

        self.hp = 5

        self.money = 0

        self.invul = 0

        # БЕЗОПАСНЫЙ СПАВН
        self.safe_spawn_x = x
        self.safe_spawn_y = y

        # ТАЙМЕР РЕСПАВНА
        self.respawn_timer = 0

        # АНИМАЦИЯ ПРЫЖКА
        self.jump_rotation = 0

    def update(self,keys,platforms):

        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            return

        if keys[pygame.K_LEFT]:
            self.vel_x -= self.acceleration

        if keys[pygame.K_RIGHT]:
            self.vel_x += self.acceleration

        self.vel_x *= self.friction

        if self.vel_x > self.max_speed:
            self.vel_x = self.max_speed

        if self.vel_x < -self.max_speed:
            self.vel_x = -self.max_speed

        if keys[pygame.K_UP] and self.on_ground:

            self.vy = self.jump

            self.jump_rotation = 20

            jump_sound.set_volume(MASTER_VOLUME)
            jump_sound.play()

        self.vy += self.gravity

        self.rect.x += self.vel_x

        self.collide(platforms,"x")

        self.rect.y += self.vy

        self.on_ground = False

        self.collide(platforms,"y")

        if self.invul > 0:
            self.invul -= 1

        # =================================================
        # АНИМАЦИЯ ПРЫЖКА
        # =================================================

        if not self.on_ground:

            self.jump_rotation *= 0.92

            self.image = pygame.transform.rotate(
                self.base_image,
                self.jump_rotation
            )

            center = self.rect.center
            self.rect = self.image.get_rect(center=center)

        else:

            self.image = self.base_image.copy()
            self.jump_rotation = 0

    def collide(self,platforms,dir):

        hits = pygame.sprite.spritecollide(
            self,
            platforms,
            False
        )

        for p in hits:

            if dir == "x":

                if self.vel_x > 0:
                    self.rect.right = p.rect.left

                if self.vel_x < 0:
                    self.rect.left = p.rect.right

            else:

                if self.vy > 0:

                    self.rect.bottom = p.rect.top

                    self.vy = 0

                    self.on_ground = True

                    # СОХРАНЯЕМ БЕЗОПАСНУЮ ТОЧКУ
                    self.safe_spawn_x = self.rect.x
                    self.safe_spawn_y = self.rect.y

                if self.vy < 0:

                    self.rect.top = p.rect.bottom

                    self.vy = 0

# =========================================================
# GAME
# =========================================================

class Game:

    def __init__(self):

        self.state = "MENU"

        self.level = 1

        self.difficulty = "NORMAL"

        self.music_timer = 0

        self.create_groups()

    def create_groups(self):

        self.all_sprites = pygame.sprite.Group()

        self.platforms = pygame.sprite.Group()

        self.spikes = pygame.sprite.Group()

        self.enemies = pygame.sprite.Group()

        self.coins = pygame.sprite.Group()

    # =====================================================
    # LEVEL
    # =====================================================

    def generate_level(self,level):

        self.create_groups()

        x = 200

        last_y = 500

        for i in range(20 + level*2):

            w = random.randint(180,320)

            offset = random.randint(-100,100)

            y = last_y + offset

            y = max(250,min(580,y))

            last_y = y

            p = Platform(x,y,w,34)

            self.platforms.add(p)
            self.all_sprites.add(p)

            if random.random() < 0.7:

                enemy = Enemy(
                    x + 40,
                    y - 64,
                    DIFFICULTY[self.difficulty]["enemy_speed"]
                )

                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

            for c in range(random.randint(1,3)):

                coin = Coin(
                    x + random.randint(20,w-30),
                    y - 60
                )

                self.coins.add(coin)
                self.all_sprites.add(coin)

            if random.random() < 0.5:

                spike = Spike(
                    x + w//2,
                    y - 30
                )

                self.spikes.add(spike)
                self.all_sprites.add(spike)

            gap = random.randint(150,260)

            x += w + gap

        self.player = Player(120,500)

        self.all_sprites.add(self.player)

    # =====================================================
    # MUSIC LOOP
    # =====================================================

    def play_music(self):

        self.music_timer += 1

        if self.music_timer >= 30:

            self.music_timer = 0

            note = random.choice(music_notes)

            note.set_volume(MASTER_VOLUME * 0.4)

            note.play()

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self,keys):

        self.play_music()

        self.player.update(
            keys,
            self.platforms
        )

        self.enemies.update(self.platforms)

        self.cam_x = max(
            0,
            self.player.rect.x - WIDTH//3
        )

        # =================================================
        # ПАДЕНИЕ
        # =================================================

        if self.player.rect.top > HEIGHT + 200:

            hurt_sound.set_volume(MASTER_VOLUME)
            hurt_sound.play()

            self.player.hp -= 1

            # БЕЗОПАСНЫЙ РЕСПАВН
            self.player.rect.x = self.player.safe_spawn_x
            self.player.rect.y = self.player.safe_spawn_y - 50

            self.player.vy = 0
            self.player.vel_x = 0

            self.player.invul = 180
            self.player.respawn_timer = 60

        # =================================================
        # COINS
        # =================================================

        coins = pygame.sprite.spritecollide(
            self.player,
            self.coins,
            True
        )

        if coins:

            coin_sound.set_volume(MASTER_VOLUME)
            coin_sound.play()

        self.player.money += len(coins) * 5

        # =================================================
        # SPIKES
        # =================================================

        if pygame.sprite.spritecollideany(
            self.player,
            self.spikes
        ):

            if self.player.invul <= 0:

                hurt_sound.set_volume(MASTER_VOLUME)
                hurt_sound.play()

                self.player.hp -= SPIKE_DAMAGE

                self.player.invul = 90

        # =================================================
        # ENEMIES
        # =================================================

        enemies = pygame.sprite.spritecollide(
            self.player,
            self.enemies,
            False
        )

        for e in enemies:

            if (
                self.player.vy > 0 and
                self.player.rect.bottom < e.rect.top + 20
            ):

                enemy_sound.set_volume(MASTER_VOLUME)
                enemy_sound.play()

                e.kill()

                self.player.vy = -15

            else:

                if self.player.invul <= 0:

                    hurt_sound.set_volume(MASTER_VOLUME)
                    hurt_sound.play()

                    self.player.hp -= DIFFICULTY[self.difficulty]["damage"]

                    self.player.invul = 60

        if self.player.hp <= 0:

            self.state = "GAME_OVER"

        if self.player.rect.x > 7000:

            self.level += 1

            self.generate_level(self.level)

    # =====================================================
    # BACKGROUND
    # =====================================================

    def draw_background(self):

        screen.fill(SKY)

        for s in stars:

            pygame.draw.circle(
                screen,
                WHITE,
                (s[0],s[1]),
                s[2]
            )

        for b in buildings:

            x = b[0]
            h = b[1]

            pygame.draw.rect(
                screen,
                BUILDING,
                (x,HEIGHT-h,80,h)
            )

            for wy in range(HEIGHT-h+10,HEIGHT,22):

                for wx in range(x+10,x+70,18):

                    if (wx+wy)%3 == 0:

                        pygame.draw.rect(
                            screen,
                            WINDOW,
                            (wx,wy,6,10)
                        )

    # =====================================================
    # DRAW GAME
    # =====================================================

    def draw(self):

        self.draw_background()

        for s in self.all_sprites:

            r = s.rect.copy()

            r.x -= self.cam_x

            # МИГАНИЕ ПРИ НЕУЯЗВИМОСТИ
            if (
                s == self.player and
                self.player.invul > 0 and
                self.player.invul % 10 < 5
            ):
                continue

            screen.blit(s.image,r)

        lvl = font.render(
            f"LEVEL: {self.level}",
            True,
            WHITE
        )

        hp = font.render(
            f"HP: {self.player.hp}",
            True,
            RED
        )

        money = font.render(
            f"COINS: {self.player.money}",
            True,
            GOLD
        )

        volume = font.render(
            f"VOLUME: {int(MASTER_VOLUME*100)}%",
            True,
            GOLD
        )

        screen.blit(lvl,(20,20))
        screen.blit(hp,(240,20))
        screen.blit(money,(390,20))
        screen.blit(volume,(620,20))

        pygame.display.flip()

    # =====================================================
    # MENU
    # =====================================================

    def menu(self):

        screen.fill((10,10,20))

        title = big_font.render(
            "CYBER ROOFTOP",
            True,
            CYAN
        )

        subtitle = font.render(
            "ADVENTURE ULTIMATE",
            True,
            PINK
        )

        start = font.render(
            "[ENTER] START",
            True,
            WHITE
        )

        diff = font.render(
            f"[TAB] DIFFICULTY: {self.difficulty}",
            True,
            GOLD
        )

        volume = font.render(
            f"[+/-] VOLUME: {int(MASTER_VOLUME*100)}%",
            True,
            WHITE
        )

        controls = font.render(
            "ARROWS = MOVE / JUMP",
            True,
            (180,180,180)
        )

        title_rect = title.get_rect(center=(WIDTH//2, 180))
        subtitle_rect = subtitle.get_rect(center=(WIDTH//2, 250))

        start_rect = start.get_rect(center=(WIDTH//2, 370))
        diff_rect = diff.get_rect(center=(WIDTH//2, 430))
        volume_rect = volume.get_rect(center=(WIDTH//2, 490))

        controls_rect = controls.get_rect(center=(WIDTH//2, 580))

        screen.blit(title, title_rect)
        screen.blit(subtitle, subtitle_rect)

        screen.blit(start, start_rect)
        screen.blit(diff, diff_rect)
        screen.blit(volume, volume_rect)

        screen.blit(controls, controls_rect)

        pygame.display.flip()

    # =====================================================
    # GAME OVER MENU
    # =====================================================

    def game_over_menu(self):

        screen.fill((20,0,0))

        txt = big_font.render(
            "GAME OVER",
            True,
            RED
        )

        restart = font.render(
            "[R] RESTART",
            True,
            WHITE
        )

        menu = font.render(
            "[ESC] MAIN MENU",
            True,
            WHITE
        )

        screen.blit(txt,(430,240))
        screen.blit(restart,(500,380))
        screen.blit(menu,(470,440))

        pygame.display.flip()

    # =====================================================
    # RUN
    # =====================================================

    def run(self):

        global MASTER_VOLUME

        while True:

            clock.tick(FPS)

            keys = pygame.key.get_pressed()

            for e in pygame.event.get():

                if e.type == pygame.QUIT:

                    pygame.quit()
                    sys.exit()

                if self.state == "MENU":

                    if e.type == pygame.KEYDOWN:

                        if e.key == pygame.K_TAB:

                            menu_sound.play()

                            modes = list(DIFFICULTY.keys())

                            idx = modes.index(self.difficulty)

                            self.difficulty = modes[
                                (idx+1)%len(modes)
                            ]

                        if e.key == pygame.K_EQUALS:

                            MASTER_VOLUME += 0.1
                            MASTER_VOLUME = min(1.0, MASTER_VOLUME)

                        if e.key == pygame.K_MINUS:

                            MASTER_VOLUME -= 0.1
                            MASTER_VOLUME = max(0.0, MASTER_VOLUME)

                        if e.key == pygame.K_RETURN:

                            self.level = 1

                            self.generate_level(1)

                            self.state = "PLAY"

                elif self.state == "GAME_OVER":

                    if e.type == pygame.KEYDOWN:

                        if e.key == pygame.K_r:

                            self.level = 1

                            self.generate_level(1)

                            self.state = "PLAY"

                        if e.key == pygame.K_ESCAPE:

                            self.state = "MENU"

            if self.state == "MENU":

                self.menu()

            elif self.state == "PLAY":

                self.update(keys)

                self.draw()

            elif self.state == "GAME_OVER":

                self.game_over_menu()

# =========================================================
# START
# =========================================================

game = Game()

game.run()
