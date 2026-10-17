import math

import pygame

from src.core import settings
from src.logic import blocks
from src.scenes import play_scene
from src.scenes.base_scene import BaseScene
from src.ui.board import Board
from src.ui.button import ImageButton
from src.ui.label import FlashMessage, Label
from src.ui.program_editor import ProgramEditor


class PlanScene(BaseScene):
    def __init__(self, game, session):
        super().__init__(game, session)
        self.overview_board = Board(session.level, settings.PLAN_OVERVIEW_MAP_RECT, session.ghost_count)
        self.edit_board = Board(session.level, settings.PLAN_MAP_RECT, session.ghost_count)
        self.programs = session.programs
        self.time_left = float(session.planning_time)
        self.selected_ghost = None
        self.cancel_key = pygame.key.key_code(settings.KEY_CANCEL)
        lock_x, lock_y = settings.PLAN_LOCK_BUTTON_POS
        flash = FlashMessage((pygame.Rect(settings.PALETTE_RECT).centerx, lock_y), settings.FONT_SMALL)
        self.editor = ProgramEditor(session.config["block_limit"], flash)
        self.timer = Label("", (0, settings.PLAN_TITLE_Y), settings.FONT_LARGE, anchor="center")
        self.hint = Label(
            "Click a ghost to program it",
            (self.editor.program_rect.right, settings.PLAN_TITLE_Y),
            settings.FONT_MEDIUM,
            settings.TEXT_DIM_COLOR,
            "midright",
        )
        self.ui = [self.timer, self.hint, ImageButton((lock_x, lock_y), self.lock, "Lock & Run"), flash]
        self.refresh_labels()

    @property
    def board(self) -> Board:
        return self.overview_board if self.selected_ghost is None else self.edit_board

    def select_ghost(self, index: int):
        self.selected_ghost = index
        self.overview_board.select_ghost(index)
        self.edit_board.select_ghost(index)
        self.editor.edit(index, self.programs[index])
        self.refresh_labels()

    def refresh_labels(self):
        self.hint.visible = self.selected_ghost is None
        self.timer.position = (self.board.map_view.area.centerx, settings.PLAN_TITLE_Y)
        seconds = max(0, math.ceil(self.time_left))
        color = settings.WARNING_COLOR if self.time_left < settings.TIMER_WARNING_SECONDS else settings.TEXT_COLOR
        self.timer.set_text(f"{seconds // 60}:{seconds % 60:02d}", color)

    def lock(self):
        first_attempt = not self.session.trees
        self.session.trees = [blocks.parse(program) for program in self.programs]
        self.session.seconds_left = max(0.0, self.time_left) if first_attempt else 0.0
        self.game.change_scene(play_scene.PlayScene(self.game, self.session))

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == self.cancel_key:
            self.editor.cancel()
            return
        if self.forward_event(event):
            return
        if self.selected_ghost is not None and self.editor.handle_event(event):
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            ghost = self.board.ghost_at(event.pos)
            if ghost is not None:
                self.select_ghost(ghost)

    def update(self, dt: float):
        self.time_left -= dt
        if self.time_left <= 0:
            self.lock()
            return
        self.refresh_labels()
        self.board.update(dt)
        self.editor.update(dt)
        self.update_ui(dt)

    def draw(self, surface: pygame.Surface):
        surface.fill(settings.BG_COLOR)
        route = self.session.route_tiles if self.session.config["preview"] else ()
        self.board.draw(surface, self.session.start_pellets(), route)
        self.draw_ui(surface)
        if self.selected_ghost is not None:
            self.editor.draw(surface)
