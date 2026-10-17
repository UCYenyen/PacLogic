"""Safe, cached loading of images, sounds, fonts, and music.

Every loader falls back to a usable placeholder instead of crashing, so a
missing or broken asset never takes the game down.
"""
from functools import lru_cache
from pathlib import Path

import pygame

from src.core import settings


class _SilentSound:
    """Stand-in for pygame.mixer.Sound when audio is unavailable."""

    def play(self, *args, **kwargs):
        return None

    def set_volume(self, *args, **kwargs):
        return None


def _mixer_ready() -> bool:
    return pygame.mixer.get_init() is not None


@lru_cache(maxsize=None)
def load_image(relative_path: str, alpha: bool = True) -> pygame.Surface:
    """Load an image from assets/images/. Returns a magenta placeholder on failure."""
    path = settings.IMAGES_DIR / relative_path
    try:
        image = pygame.image.load(str(path))
        if pygame.display.get_surface() is not None:
            image = image.convert_alpha() if alpha else image.convert()
        return image
    except (pygame.error, FileNotFoundError) as exc:
        print(f"[resource_loader] Could not load image '{path}': {exc}")
        placeholder = pygame.Surface((32, 32))
        placeholder.fill((255, 0, 255))
        return placeholder


@lru_cache(maxsize=None)
def load_sound(relative_path: str, volume: float = 1.0):
    """Load a sound effect from assets/sounds/. Returns a silent stub on failure."""
    if not _mixer_ready():
        return _SilentSound()
    path = settings.SOUNDS_DIR / relative_path
    try:
        sound = pygame.mixer.Sound(str(path))
        sound.set_volume(volume)
        return sound
    except (pygame.error, FileNotFoundError) as exc:
        print(f"[resource_loader] Could not load sound '{path}': {exc}")
        return _SilentSound()


@lru_cache(maxsize=None)
def load_font(size: int, relative_path: str = "default.ttf") -> pygame.font.Font:
    """Load a font from assets/fonts/. Falls back to pygame's built-in font."""
    path = settings.FONTS_DIR / relative_path
    try:
        return pygame.font.Font(str(path), size)
    except (pygame.error, FileNotFoundError, OSError) as exc:
        print(f"[resource_loader] Could not load font '{path}': {exc}")
        return pygame.font.Font(None, size)


def play_music(relative_path: str, volume: float = 0.5, loops: int = -1) -> None:
    """Stream background music from assets/sounds/. Silently skips on failure."""
    if not _mixer_ready():
        return
    path: Path = settings.SOUNDS_DIR / relative_path
    try:
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops)
    except (pygame.error, FileNotFoundError) as exc:
        print(f"[resource_loader] Could not play music '{path}': {exc}")
