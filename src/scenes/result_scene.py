import pygame

from src.core import settings
from src.core.resource_loader import load_scaled_image
from src.logic.sim import BLOCKED, CAUGHT, ESCAPED, score_breakdown, total_score
from src.scenes import menu_scene, plan_scene, play_scene
from src.scenes.base_scene import BaseScene
from src.ui.button import ImageButton
from src.ui.label import Label
from src.ui.panel import Panel

OUTCOME_TEXT = {
    CAUGHT: "The ghosts caught Pac-Man!",
    ESCAPED: "Pac-Man escaped.",
    BLOCKED: "Time ran out. Pac-Man is blocked.",
}
OUTCOME_BANNERS = {
    CAUGHT: settings.UI_BANNER_CAUGHT,
    ESCAPED: settings.UI_BANNER_ESCAPED,
    BLOCKED: settings.UI_BANNER_BLOCKED,
}


class ResultScene(BaseScene):
    def __init__(self, game, session, sim):
        super().__init__(game, session)
        center_x = settings.SCREEN_WIDTH // 2
        self.banner = load_scaled_image(
            OUTCOME_BANNERS[sim.status], settings.UI_SCALE, settings.BANNER_PLACEHOLDER_SIZE
        )
        self.banner_rect = self.banner.get_rect(center=(center_x, settings.RESULT_BANNER_Y))
        breakdown = score_breakdown(sim, session.seconds_left)
        panel = Panel(settings.RESULT_PANEL_RECT)
        rows = [
            Label(name, (panel.rect.x + 30, panel.rect.y + 30 + row * 40))
            for row, (name, _) in enumerate(breakdown)
        ]
        rows += [
            Label(str(points), (panel.rect.right - 30, panel.rect.y + 30 + row * 40), anchor="topright")
            for row, (_, points) in enumerate(breakdown)
        ]
        self.ui = [
            Label(OUTCOME_TEXT[sim.status], (center_x, settings.RESULT_TEXT_Y), settings.FONT_MEDIUM, settings.TEXT_DIM_COLOR, "center"),
            panel,
            *rows,
            Label("Total", (panel.rect.x + 30, panel.rect.bottom - 60), settings.FONT_LARGE, settings.ACCENT_COLOR),
            Label(
                str(total_score(breakdown)),
                (panel.rect.right - 30, panel.rect.bottom - 60),
                settings.FONT_LARGE,
                settings.ACCENT_COLOR,
                "topright",
            ),
            ImageButton((center_x - settings.RESULT_BUTTON_SPACING, settings.RESULT_BUTTON_Y), self.replay, "Replay"),
            ImageButton((center_x, settings.RESULT_BUTTON_Y), self.edit_programs, "Edit programs"),
            ImageButton((center_x + settings.RESULT_BUTTON_SPACING, settings.RESULT_BUTTON_Y), self.menu, "Menu"),
        ]

    def replay(self):
        self.game.change_scene(play_scene.PlayScene(self.game, self.session))

    def edit_programs(self):
        self.game.change_scene(plan_scene.PlanScene(self.game, self.session))

    def menu(self):
        self.game.change_scene(menu_scene.MenuScene(self.game, self.session))

    def handle_event(self, event: pygame.event.Event):
        self.forward_event(event)

    def update(self, dt: float):
        self.update_ui(dt)

    def draw(self, surface: pygame.Surface):
        surface.fill(settings.BG_COLOR)
        surface.blit(self.banner, self.banner_rect)
        self.draw_ui(surface)
