import pygame

from src.core import settings
from src.core.resource_loader import load_scaled_image
from src.ui.component import Component


class Image(Component):
    def __init__(
        self,
        path: str,
        position,
        scale: int = settings.UI_SCALE,
        anchor: str = "center",
        fallback_size: tuple[int, int] | None = None,
    ):
        self.image = load_scaled_image(path, scale, fallback_size)
        self.rect = self.image.get_rect(**{anchor: position})

    def draw(self, surface: pygame.Surface):
        if self.visible:
            surface.blit(self.image, self.rect)
