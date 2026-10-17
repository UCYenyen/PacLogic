"""Global constants: screen size, FPS, colors, key bindings, asset paths."""
from pathlib import Path

import pygame

# --- Window ---
TITLE = "My Pygame Game"
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60

# --- Paths ---
ROOT_DIR = Path(__file__).resolve().parents[2]
ASSETS_DIR = ROOT_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
IMAGES_DIR = ASSETS_DIR / "images"
SOUNDS_DIR = ASSETS_DIR / "sounds"

# --- Colors (R, G, B) ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BG_COLOR = (24, 26, 38)
GROUND_COLOR = (58, 64, 92)
ACCENT = (255, 204, 0)
RED = (220, 60, 60)
GREEN = (80, 200, 120)

# --- Physics ---
GRAVITY = 1800.0          # px / s^2
PLAYER_SPEED = 300.0      # px / s
PLAYER_JUMP_SPEED = 700.0 # px / s
ENEMY_SPEED = 160.0       # px / s
GROUND_Y = SCREEN_HEIGHT - 60

# --- Gameplay ---
PLAYER_LIVES = 3
INVULNERABLE_TIME = 1.5   # seconds after taking a hit
ENEMY_SPAWN_INTERVAL = 2.0

# --- Key bindings ---
KEYS_LEFT = (pygame.K_LEFT, pygame.K_a)
KEYS_RIGHT = (pygame.K_RIGHT, pygame.K_d)
KEYS_JUMP = (pygame.K_SPACE, pygame.K_UP, pygame.K_w)
KEYS_CONFIRM = (pygame.K_RETURN, pygame.K_SPACE)
KEY_PAUSE = pygame.K_ESCAPE
