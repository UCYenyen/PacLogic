from functools import lru_cache

import pygame

from src.core import settings


class _SilentSound:
    def play(self, *args, **kwargs) -> None:
        return None

    def set_volume(self, *args, **kwargs) -> None:
        return None


def _mixer_ready() -> bool:
    return pygame.mixer.get_init() is not None


def _placeholder_image() -> pygame.Surface:
    placeholder = pygame.Surface(settings.PLACEHOLDER_SIZE)
    placeholder.fill(settings.PLACEHOLDER_COLOR)
    return placeholder


@lru_cache(maxsize=None)
def load_image(relative_path: str, alpha: bool = True) -> pygame.Surface:
    path = settings.IMAGES_DIR / relative_path
    try:
        image = pygame.image.load(str(path))
    except (pygame.error, FileNotFoundError) as exc:
        print(f"[resource_loader] Could not load image '{path}': {exc}")
        return _placeholder_image()
    if pygame.display.get_surface() is None:
        return image
    return image.convert_alpha() if alpha else image.convert()


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


def play_music(relative_path: str, volume: float = 0.5, loops: int = -1) -> None:
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
