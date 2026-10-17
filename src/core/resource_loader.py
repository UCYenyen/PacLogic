import re
from functools import lru_cache

import pygame

from src.core import settings

FRAME_NUMBER = re.compile(r"(\d+)$")


class _SilentSound:
    def play(self, *args, **kwargs):
        return None

    def set_volume(self, *args, **kwargs):
        return None


def _mixer_ready() -> bool:
    return pygame.mixer.get_init() is not None


def _placeholder_image(size: tuple[int, int] | None = None) -> pygame.Surface:
    placeholder = pygame.Surface(size or settings.PLACEHOLDER_SIZE)
    placeholder.fill(settings.PLACEHOLDER_COLOR)
    return placeholder


@lru_cache(maxsize=None)
def load_image(relative_path: str, alpha: bool = True, fallback_size: tuple[int, int] | None = None) -> pygame.Surface:
    path = settings.IMAGES_DIR / relative_path
    try:
        image = pygame.image.load(str(path))
    except (pygame.error, FileNotFoundError) as exc:
        print(f"[resource_loader] Could not load image '{path}': {exc}")
        return _placeholder_image(fallback_size)
    if pygame.display.get_surface() is None:
        return image
    return image.convert_alpha() if alpha else image.convert()


@lru_cache(maxsize=None)
def load_scaled_image(relative_path: str, scale: int, fallback_size: tuple[int, int] | None = None) -> pygame.Surface:
    image = load_image(relative_path, True, fallback_size)
    if scale == 1:
        return image
    return pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))


def _frame_sort_key(path) -> tuple[int, str]:
    match = FRAME_NUMBER.search(path.stem)
    return (int(match.group(1)) if match else 0, path.stem)


@lru_cache(maxsize=None)
def load_animation(folder: str, scale: int = settings.ART_SCALE) -> tuple:
    directory = settings.IMAGES_DIR / folder
    fallback = (settings.TILE_SIZE, settings.TILE_SIZE)
    paths = sorted(directory.glob("*.png"), key=_frame_sort_key) if directory.is_dir() else []
    if not paths:
        print(f"[resource_loader] No animation frames in '{directory}'")
        return (load_scaled_image(f"{folder}/missing.png", scale, fallback),)
    return tuple(
        load_scaled_image(path.relative_to(settings.IMAGES_DIR).as_posix(), scale, fallback)
        for path in paths
    )


def has_frames(folder: str) -> bool:
    directory = settings.IMAGES_DIR / folder
    return directory.is_dir() and any(directory.glob("*.png"))


def list_folders(relative_path: str) -> list:
    directory = settings.IMAGES_DIR / relative_path
    if not directory.is_dir():
        return []
    return sorted(child.name for child in directory.iterdir() if child.is_dir())


@lru_cache(maxsize=None)
def load_sound(relative_path: str, volume: float = 1.0) -> pygame.mixer.Sound | _SilentSound:
    if not _mixer_ready():
        return _SilentSound()
    path = settings.SOUNDS_DIR / relative_path
    try:
        sound = pygame.mixer.Sound(str(path))
    except (pygame.error, FileNotFoundError) as exc:
        print(f"[resource_loader] Could not load sound '{path}': {exc}")
        return _SilentSound()
    sound.set_volume(volume)
    return sound


@lru_cache(maxsize=None)
def load_font(size: int, relative_path: str = settings.DEFAULT_FONT) -> pygame.font.Font:
    path = settings.FONTS_DIR / relative_path
    try:
        return pygame.font.Font(str(path), size)
    except (pygame.error, FileNotFoundError, OSError) as exc:
        print(f"[resource_loader] Could not load font '{path}': {exc}")
        return pygame.font.Font(None, size)


def play_music(relative_path: str, volume: float = 0.5, loops: int = -1):
    if not _mixer_ready():
        return
    path = settings.SOUNDS_DIR / relative_path
    try:
        pygame.mixer.music.load(str(path))
    except (pygame.error, FileNotFoundError) as exc:
        print(f"[resource_loader] Could not play music '{path}': {exc}")
        return
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(loops)
