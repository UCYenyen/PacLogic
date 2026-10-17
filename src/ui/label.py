import pygame

from src.core import settings
from src.core.resource_loader import load_font
from src.ui.component import Component


class Label(Component):
    def __init__(self, text: str, position, size: int = settings.FONT_MEDIUM, color=settings.TEXT_COLOR, anchor: str = "topleft"):
        self.font = load_font(size)
        self.position = position
        self.anchor = anchor
        self.text = None
        self.color = color
        self.image = None
        self.set_text(text)

    def set_text(self, text: str, color=None):
        color = color or self.color
        if text == self.text and color == self.color and self.image is not None:
            return
        self.text = text
        self.color = color
        self.image = self.font.render(text, True, color)

    @property
    def rect(self) -> pygame.Rect:
        return self.image.get_rect(**{self.anchor: self.position})

    def draw(self, surface: pygame.Surface):
        if self.visible:
            surface.blit(self.image, self.rect)


class FlashMessage(Label):
    def __init__(self, position, size: int = settings.FONT_MEDIUM, color=settings.WARNING_COLOR):
        super().__init__("", position, size, color, anchor="center")
        self.time_left = 0.0

    def show(self, text: str, seconds: float = settings.FLASH_DURATION):
        self.set_text(text)
        self.time_left = seconds

    def update(self, dt: float):
        self.time_left = max(0.0, self.time_left - dt)

    def draw(self, surface: pygame.Surface):
        if self.time_left > 0:
            super().draw(surface)
