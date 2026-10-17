import pygame

from src.core import settings
from src.core.resource_loader import has_frames, list_folders, load_animation
from src.entities.animator import load_directional_animator
from src.entities.player import lerp_tile


def ghost_art_ready(name: str) -> bool:
    base = f"{settings.GHOST_SPRITE_DIR}/{name}"
    return all(
        has_frames(f"{base}/{settings.GHOST_ACTION}-{direction}")
        for direction in settings.DIRECTION_NAMES.values()
    )


def ghost_art_folders(count: int) -> tuple[list, list]:
    ordered = [name for name in settings.GHOST_ORDER if ghost_art_ready(name)]
    extras = [
        name
        for name in list_folders(settings.GHOST_SPRITE_DIR)
        if name not in settings.GHOST_ORDER and ghost_art_ready(name)
    ]
    available = ordered + extras or [settings.GHOST_ORDER[0]]
    missing = [name for name in settings.GHOST_ORDER[:count] if name not in available]
    folders = [f"{settings.GHOST_SPRITE_DIR}/{available[index % len(available)]}" for index in range(count)]
    return folders, missing


class Enemy(pygame.sprite.Sprite):
    def __init__(self, folder: str, scale: int):
        super().__init__()
        self.folder = folder
        self.animator = load_directional_animator(
            folder,
            settings.GHOST_ACTION,
            scale,
            settings.GHOST_FRAME_DURATION,
            settings.GHOST_START_DIRECTION,
        )
        self.selected_image = load_animation(f"{folder}/{settings.GHOST_SELECTED_FOLDER}", scale)[0]
        self.selected = False
        self.image = self.animator.image
        self.rect = self.image.get_rect()

    def follow(self, previous_tile, tile, direction: str | None, progress: float, map_view):
        self.animator.set_direction(direction)
        self.rect.center = map_view.tile_center(*lerp_tile(previous_tile, tile, progress))

    def update(self, dt: float):
        self.animator.update(dt)
        self.image = self.selected_image if self.selected else self.animator.image
