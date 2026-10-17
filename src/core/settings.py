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
DEFAULT_FONT = "default.ttf"

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BG_COLOR = (24, 26, 38)
PLACEHOLDER_COLOR = (255, 0, 255)
PLACEHOLDER_SIZE = (32, 32)
