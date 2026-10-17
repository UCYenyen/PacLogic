from functools import partial

import pygame

from src.core import settings
from src.core.resource_loader import has_image
from src.logic.grid import LevelError
from src.scenes import preview_scene
from src.scenes.base_scene import BaseScene
from src.ui.button import ImageButton
from src.ui.image import Image
from src.ui.label import FlashMessage, Label
from src.ui.panel import Panel

OPTIONS = ("level", "ai", "ghosts", "mode", "time")


class MenuScene(BaseScene):
    def __init__(self, game, session):
        super().__init__(game, session)
        self.cancel_key = pygame.key.key_code(settings.KEY_CANCEL)
        center_x = settings.SCREEN_WIDTH // 2
        self.main_ui = [
            Image(settings.MENU_LOGO, (center_x, 200), settings.MENU_SCALE),
            ImageButton(
                (center_x, 430),
                self.open_setup,
                images=(settings.MENU_PLAY_BUTTON,) * 3,
                scale=settings.MENU_SCALE,
            ),
            ImageButton(
                (center_x, 510),
                self.game.quit,
                images=(settings.MENU_QUIT_BUTTON,) * 3,
                scale=settings.MENU_SCALE,
            ),
        ]
        modal = Panel(settings.SETUP_MODAL_RECT)
        self.option_boxes = {
            option: Image(
                settings.MENU_OPTION_BOX,
                (center_x, modal.rect.y + 140 + row * 60),
                fallback_size=settings.OPTION_PLACEHOLDER_SIZE,
            )
            for row, option in enumerate(OPTIONS)
        }
        self.option_labels = {
            option: Label("", box.rect.center, settings.FONT_MEDIUM, anchor="center")
            for option, box in self.option_boxes.items()
        }
        self.arrow_buttons = [
            arrow
            for option in OPTIONS
            for arrow in (
                self.arrow_button(settings.MENU_ARROW_LEFT, "<", "midright", option, -1),
                self.arrow_button(settings.MENU_ARROW_RIGHT, ">", "midleft", option, 1),
            )
        ]
        self.flash = FlashMessage((center_x, modal.rect.bottom + 40))
        self.setup_ui = [
            modal,
            Label("Game setup", (center_x, modal.rect.y + 44), settings.FONT_LARGE, settings.ACCENT_COLOR, "center"),
            *self.option_boxes.values(),
            *self.option_labels.values(),
            *self.arrow_buttons,
            ImageButton((center_x - 120, modal.rect.bottom - 56), self.close_setup, "Back"),
            ImageButton((center_x + 120, modal.rect.bottom - 56), self.start_game, "Continue"),
            self.flash,
        ]
        self.dim = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.dim.fill(settings.MODAL_DIM_COLOR)
        self.setup_open = False
        self.ui = self.main_ui
        self.refresh()

    def arrow_button(self, image: str, fallback_text: str, anchor: str, option: str, delta: int) -> ImageButton:
        box = self.option_boxes[option].rect
        x = box.left - settings.ARROW_GAP if anchor == "midright" else box.right + settings.ARROW_GAP
        return ImageButton(
            (x, box.centery),
            partial(self.cycle, option, delta),
            "" if has_image(image) else fallback_text,
            anchor=anchor,
            images=(image,) * 3,
            fallback_size=settings.ARROW_PLACEHOLDER_SIZE,
        )

    def open_setup(self):
        self.setup_open = True
        self.ui = self.setup_ui

    def close_setup(self):
        self.setup_open = False
        self.ui = self.main_ui

    def cycle(self, option: str, delta: int):
        self.session.cycle(option, delta)
        self.refresh()

    def refresh(self):
        for option, label in self.option_labels.items():
            label.set_text(self.session.option_text(option))

    def start_game(self):
        try:
            self.session.prepare()
        except LevelError as error:
            self.flash.show(str(error))
            return
        self.game.change_scene(preview_scene.PreviewScene(self.game, self.session))

    def handle_event(self, event: pygame.event.Event):
        if self.setup_open and event.type == pygame.KEYDOWN and event.key == self.cancel_key:
            self.close_setup()
            return
        self.forward_event(event)

    def update(self, dt: float):
        self.update_ui(dt)

    def draw(self, surface: pygame.Surface):
        surface.fill(settings.BG_COLOR)
        for component in self.main_ui:
            component.draw(surface)
        if self.setup_open:
            surface.blit(self.dim, (0, 0))
            self.draw_ui(surface)
