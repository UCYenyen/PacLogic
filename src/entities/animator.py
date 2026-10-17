import pygame

from src.core import settings
from src.core.resource_loader import load_animation


class Animator:
    def __init__(self, animations: dict, frame_duration: float, direction: str):
        self.animations = animations
        self.frame_duration = frame_duration
        self.direction = direction
        self.frame_index = 0
        self.elapsed = 0.0

    def set_direction(self, direction: str | None):
        if direction is None or direction == self.direction or direction not in self.animations:
            return
        self.direction = direction
        self.frame_index = 0
        self.elapsed = 0.0

    def update(self, dt: float):
        frames = self.animations[self.direction]
        self.elapsed += dt
        while self.elapsed >= self.frame_duration:
            self.elapsed -= self.frame_duration
            self.frame_index = (self.frame_index + 1) % len(frames)

    @property
    def image(self) -> pygame.Surface:
        return self.animations[self.direction][self.frame_index]


def load_directional_animator(base_folder: str, action: str, scale: int, frame_duration: float, direction: str) -> Animator:
    animations = {
        code: load_animation(f"{base_folder}/{action}-{name}", scale)
        for code, name in settings.DIRECTION_NAMES.items()
    }
    return Animator(animations, frame_duration, direction)
