"""Simple enemy that walks across the ground and despawns off-screen."""
import pygame

from src.core import settings
from src.core.resource_loader import load_image


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x: float, direction: int, speed: float = settings.ENEMY_SPEED) -> None:
        super().__init__()
        self.image = load_image("sprites/enemy.png")
        if direction > 0:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(midbottom=(x, settings.GROUND_Y))
        self.pos_x = float(self.rect.centerx)
        self.direction = 1 if direction > 0 else -1
        self.speed = speed

    def update(self, dt: float) -> None:
        self.pos_x += self.direction * self.speed * dt
        self.rect.centerx = round(self.pos_x)
        if self.rect.right < -50 or self.rect.left > settings.SCREEN_WIDTH + 50:
            self.kill()
