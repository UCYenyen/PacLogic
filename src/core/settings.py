from pathlib import Path

TITLE = "PacLogic"
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
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

TILE_WALL = "sprites/tile/wall-tile.png"
TILE_FLOOR = "sprites/tile/empty-tile.png"
TILE_PELLET = "sprites/items/pellet/pellet.png"
TILE_ROUTE = "sprites/tile/path/path-preview.png"
TILE_EXIT = "sprites/tile/exit-tile.png"
TILE_SAFE_ZONE = "sprites/tile/pac-man-safe-zone.png"
TILE_GOTO_TARGET = "sprites/tile/goto-target.png"

PREVIEW_MAP_RECT = (24, 24, 820, 672)
PLAN_MAP_RECT = (16, 72, 680, 632)
PLAN_OVERVIEW_MAP_RECT = (16, 64, 1040, 640)
PLAN_LOCK_BUTTON_POS = (1164, 672)
PLAY_MAP_RECT = (24, 24, 900, 672)

UI_SCALE = 2
UI_BUTTON_IMAGES = (
    "ui/button/button-normal.png",
    "ui/button/button-hover.png",
    "ui/button/button-pressed.png",
)
MENU_SCALE = 4
MENU_LOGO = "ui/main-menu/pac-logic-logo.png"
MENU_PLAY_BUTTON = "ui/main-menu/play-button.png"
MENU_QUIT_BUTTON = "ui/main-menu/quit-button.png"
MENU_OPTION_BOX = "ui/main-menu/option-box.png"
MENU_ARROW_LEFT = "ui/main-menu/arrow-left.png"
MENU_ARROW_RIGHT = "ui/main-menu/arrow-right.png"
ARROW_PLACEHOLDER_SIZE = (12, 20)
OPTION_PLACEHOLDER_SIZE = (130, 20)
ARROW_GAP = 12
SETUP_MODAL_RECT = (360, 100, 560, 540)
MODAL_DIM_COLOR = (0, 0, 0, 170)
UI_PANEL = "ui/panel.png"
UI_PANEL_BORDER = 4
UI_BANNERS = {
    "caught": "ui/banner-caught.png",
    "escaped": "ui/banner-escaped.png",
    "blocked": "ui/banner-blocked.png",
}
UI_BLOCKS = {
    "MOVE": "ui/blocks/move.png",
    "WAIT": "ui/blocks/wait.png",
    "REPEAT": "ui/blocks/repeat.png",
    "END": "ui/blocks/end.png",
    "IF": "ui/blocks/if.png",
    "ELSE": "ui/blocks/else.png",
    "GOTO": "ui/blocks/goto.png",
}
UI_BLOCK_SELECTED = "ui/blocks/selected.png"

BUTTON_PLACEHOLDER_SIZE = (100, 20)
BLOCK_PLACEHOLDER_SIZE = (90, 11)
BANNER_PLACEHOLDER_SIZE = (160, 32)
PANEL_PLACEHOLDER_SIZE = (12, 12)

TEXT_COLOR = WHITE
TEXT_DIM_COLOR = (150, 156, 180)
WARNING_COLOR = (255, 80, 80)
ACCENT_COLOR = (255, 204, 0)
FONT_SMALL = 16
FONT_MEDIUM = 22
FONT_LARGE = 44
FLASH_DURATION = 3.0

PLANNING_TIMES = (60, 90, 120, 180)
WIN_MODES = ("Goal only", "Goal + pellets")
TIMER_WARNING_SECONDS = 10
RESULT_DELAY = 0.6

KEY_PAUSE = "space"
KEY_SPEED = "f"
KEY_CANCEL = "escape"

INFO_PANEL_RECT = (868, 24, 388, 672)
HUD_PANEL_RECT = (948, 24, 308, 672)
PALETTE_RECT = (704, 72, 208, 560)
PROGRAM_RECT = (920, 72, 344, 560)
PANEL_PADDING = 12
BLOCK_GAP = 6
ROW_HEIGHT = 26
INDENT = 18
DRAG_THRESHOLD = 6
SCROLL_STEP = 26

PACMAN_FRAME_DURATION = 0.08
GHOST_FRAME_DURATION = 0.18
