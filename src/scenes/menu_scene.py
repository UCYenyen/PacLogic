from functools import partial

import pygame

from src.core import settings
from src.logic.grid import LevelError
from src.scenes import preview_scene
from src.scenes.base_scene import BaseScene
from src.ui.button import ImageButton
from src.ui.label import FlashMessage, Label

OPTIONS = ("level", "ai", "ghosts", "mode", "time")


class MenuScene(BaseScene):
    def __init__(self, game, session):
        super().__init__(game)
        self.session = session
        center_x = settings.SCREEN_WIDTH // 2
        self.option_buttons = {
            option: ImageButton(
                (center_x, 210 + row * 60),
                on_click=partial(self.cycle, option, 1),
                on_right_click=partial(self.cycle, option, -1),
            )
            for row, option in enumerate(OPTIONS)
        }
        self.flash = FlashMessage((center_x, 680))
        self.ui = [
            Label(settings.TITLE, (center_x, 90), settings.FONT_LARGE, settings.ACCENT_COLOR, "center"),
            Label("Left click: next   Right click: previous", (center_x, 150), settings.FONT_SMALL, settings.TEXT_DIM_COLOR, "center"),
            *self.option_buttons.values(),
            ImageButton((center_x - 120, 560), self.start_game, "Start"),
            ImageButton((center_x + 120, 560), self.game.quit, "Quit"),
            self.flash,
        ]
        self.refresh()

    def cycle(self, option: str, delta: int):
        self.session.cycle(option, delta)
        self.refresh()

    def refresh(self):
        for option, button in self.option_buttons.items():
            button.set_text(self.session.option_text(option))

    def start_game(self):
        try:
            self.session.prepare()
        except LevelError as error:
            self.flash.show(str(error))
            return
        self.game.change_scene(preview_scene.PreviewScene(self.game, self.session))

    def handle_event(self, event: pygame.event.Event):
        self.forward_event(event)

    def update(self, dt: float):
        self.update_ui(dt)

    def draw(self, surface: pygame.Surface):
        surface.fill(settings.BG_COLOR)
        self.draw_ui(surface)
