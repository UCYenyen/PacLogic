import pygame

from src.core import settings
from src.scenes import menu_scene, plan_scene
from src.scenes.base_scene import BaseScene
from src.ui.board import Board
from src.ui.button import ImageButton
from src.ui.label import Label
from src.ui.panel import Panel


class PreviewScene(BaseScene):
    def __init__(self, game, session):
        super().__init__(game, session)
        level = session.level
        self.board = Board(level, settings.PREVIEW_MAP_RECT, session.ghost_count)
        panel = Panel(settings.INFO_PANEL_RECT)
        left = panel.rect.x + 24
        lines = [
            f"Size: {level.width} x {level.height}",
            f"Ghosts: {session.ghost_count}",
            f"Pac-Man AI: {session.difficulty}",
            f"Win mode: {session.mode_name}",
            f"Blocks per ghost: {session.config['block_limit']}",
            f"Planning time: {session.planning_time} s",
            f"Optimal route: {session.optimal_cost} steps",
            f"Tick limit: {session.tick_cap}",
        ]
        if session.seed is not None:
            lines.append(f"Seed: {session.seed}")
        self.ui = [
            panel,
            Label(session.level_choice, (left, panel.rect.y + 24), settings.FONT_LARGE, settings.ACCENT_COLOR),
            *(Label(text, (left, panel.rect.y + 100 + row * 36)) for row, text in enumerate(lines)),
            ImageButton((panel.rect.centerx, panel.rect.bottom - 120), self.start_planning, "Start planning"),
            ImageButton((panel.rect.centerx, panel.rect.bottom - 60), self.back, "Back"),
        ]

    def start_planning(self):
        self.game.change_scene(plan_scene.PlanScene(self.game, self.session))

    def back(self):
        self.game.change_scene(menu_scene.MenuScene(self.game, self.session))

    def handle_event(self, event: pygame.event.Event):
        self.forward_event(event)

    def update(self, dt: float):
        self.board.update(dt)
        self.update_ui(dt)

    def draw(self, surface: pygame.Surface):
        surface.fill(settings.BG_COLOR)
        route = self.session.route if self.session.config["preview"] else ()
        self.board.draw(surface, self.session.start_pellets(), route)
        self.draw_ui(surface)
