from pathlib import Path

TITLE = "PacLogic"
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60
MAX_DT = 0.05

ROOT_DIR = Path(__file__).resolve().parents[2]
ASSETS_DIR = ROOT_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
IMAGES_DIR = ASSETS_DIR / "images"
SOUNDS_DIR = ASSETS_DIR / "sounds"
LEVELS_DIR = ASSETS_DIR / "levels"
DEFAULT_FONT = "default.ttf"

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BG_COLOR = (24, 26, 38)
PLACEHOLDER_COLOR = (255, 0, 255)
PLACEHOLDER_SIZE = (32, 32)

SAFE_RADIUS = 3
MAX_PELLETS = 8
MAX_GHOSTS = 4
MOVE_ORDER = "URDL"
DANGER_RADIUS = 2
DANGER_PENALTY = 4
OP_CAP = 200
TICKS_PER_SEC = 6
FAST_SPEED = 4

TICK_CAP_FACTOR = 3
TICK_CAP_BONUS = 20
PAC_START_DIRECTION = "R"
GHOST_START_DIRECTION = "U"
ARCADE_LOOKAHEAD = 4

LEVEL_FILES = {"Easy": "easy.txt", "Medium": "medium.txt", "Hard": "hard.txt"}
RANDOM_LEVELS = {"Random 15x15": (15, 15, 4), "Random 28x31": (28, 31, 8)}
BRAID_CHANCE = 0.15
GHOST_MIN_START_DISTANCE = 6

REPEAT_MIN = 2
REPEAT_MAX = 9
NEAR_MIN = 1
NEAR_MAX = 9

DIFFICULTIES = {
    "Easy": {"replan": False, "preview": True, "block_limit": 12},
    "Medium": {"replan": False, "preview": False, "block_limit": 16},
    "Hard": {"replan": True, "preview": False, "block_limit": 20},
}

SCORE = {
    "catch": 1000,
    "per_second_left": 10,
    "per_tick_left": 5,
    "blocked": 500,
    "escaped": 0,
}

TILE_SIZE = 16
ART_SCALE = 3

DIRECTION_NAMES = {"U": "up", "R": "right", "D": "down", "L": "left"}

PACMAN_SPRITE_DIR = "sprites/pacman"
PACMAN_ACTION = "eat"
GHOST_SPRITE_DIR = "sprites/ghosts"
GHOST_ACTION = "move"
GHOST_SELECTED_FOLDER = "selected"
GHOST_ORDER = ("red-ghost", "blue-ghost", "pink-ghost", "orange-ghost")

PACMAN_FRAME_DURATION = 0.08
GHOST_FRAME_DURATION = 0.18
