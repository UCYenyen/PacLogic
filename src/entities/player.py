import pygame

from src.core import settings
from src.entities.animator import load_directional_animator


def lerp_tile(previous_tile, tile, progress: float) -> tuple[float, float]:
    return (
        previous_tile[0] + (tile[0] - previous_tile[0]) * progress,
        previous_tile[1] + (tile[1] - previous_tile[1]) * progress,
    )


class Player(pygame.sprite.Sprite):
    def __init__(self, scale: int):
        super().__init__()
        self.animator = load_directional_animator(
            settings.PACMAN_SPRITE_DIR,
            settings.PACMAN_ACTION,
            scale,
            settings.PACMAN_FRAME_DURATION,
            settings.PAC_START_DIRECTION,
        )
        self.image = self.animator.image
        self.rect = self.image.get_rect()

    def follow(self, previous_tile, tile, direction: str | None, progress: float, map_view):
        self.animator.set_direction(direction)
        self.rect.center = map_view.tile_center(*lerp_tile(previous_tile, tile, progress))

    def update(self, dt: float):
        self.animator.update(dt)
        self.image = self.animator.image
