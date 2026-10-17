import pygame

from src.core import settings
from src.core.resource_loader import load_scaled_image


class Image:
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
        self.visible = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface):
        if self.visible:
            surface.blit(self.image, self.rect)
