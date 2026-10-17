import pygame

from src.core import settings
from src.core.resource_loader import load_scaled_image
from src.ui.component import Component
from src.ui.label import Label


class ImageButton(Component):
    def __init__(
        self,
        position,
        on_click=None,
        text: str = "",
        anchor: str = "center",
        images: tuple = settings.UI_BUTTON_IMAGES,
        font_size: int = settings.FONT_MEDIUM,
        fallback_size: tuple[int, int] = settings.BUTTON_PLACEHOLDER_SIZE,
        scale: int = settings.UI_SCALE,
    ):
        self.normal, self.hover, self.pressed_image = (
            load_scaled_image(path, scale, fallback_size) for path in images
        )
        self.rect = self.normal.get_rect(**{anchor: position})
        self.on_click = on_click
        self.pressed = False
        self.label = Label(text, self.rect.center, font_size, anchor="center")

    def set_text(self, text: str):
        self.label.set_text(text)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.pressed = True
            return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False
            if was_pressed and self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        if self.pressed and hovered:
            image = self.pressed_image
        elif hovered:
            image = self.hover
        else:
            image = self.normal
        surface.blit(image, self.rect)
        self.label.position = self.rect.center
        self.label.draw(surface)
