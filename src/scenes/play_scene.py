import pygame

from src.core import settings
from src.scenes.base_scene import BaseScene


class PlayScene(BaseScene):
    def __init__(self, game) -> None:
        super().__init__(game)

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(settings.BG_COLOR)
