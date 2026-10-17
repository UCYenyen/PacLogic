from functools import partial

import pygame

from src.core import settings
from src.logic.blocks import run
from src.logic.sim import RUNNING
from src.scenes import result_scene
from src.scenes.base_scene import BaseScene
from src.ui.board import Board
from src.ui.hud import HUD


class PlayScene(BaseScene):
    def __init__(self, game, session):
        super().__init__(game, session)
        self.sim = session.new_sim([partial(run, tree) for tree in session.trees])
        self.board = Board(session.level, settings.PLAY_MAP_RECT, session.ghost_count)
        self.hud = HUD()
        self.ui = [self.hud]
        self.accumulator = 0.0
        self.speed = 1
        self.paused = False
        self.finished_for = 0.0
        self.pause_key = pygame.key.key_code(settings.KEY_PAUSE)
        self.speed_key = pygame.key.key_code(settings.KEY_SPEED)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.pause_key:
                self.paused = not self.paused
            elif event.key == self.speed_key:
                self.speed = settings.FAST_SPEED if self.speed == 1 else 1
        self.forward_event(event)

    def update(self, dt: float):
        if not self.paused:
            self.accumulator += dt * settings.TICKS_PER_SEC * self.speed
            if self.sim.status == RUNNING:
                while self.accumulator >= 1 and self.sim.status == RUNNING:
                    self.accumulator -= 1
                    self.sim.step()
            if self.sim.status != RUNNING:
                self.accumulator = min(self.accumulator, 1.0)
                self.finished_for += dt
                if self.finished_for >= settings.RESULT_DELAY:
                    self.game.change_scene(result_scene.ResultScene(self.game, self.session, self.sim))
                    return
        self.board.show_sim(self.sim, self.accumulator)
        self.board.update(dt)
        self.hud.update_stats(self.sim, self.speed, self.paused)
        self.update_ui(dt)

    def draw(self, surface: pygame.Surface):
        surface.fill(settings.BG_COLOR)
        route = self.sim.brain.future_tiles(self.sim.pac) if self.session.config["preview"] else ()
        self.board.draw(surface, self.sim.pellets, route)
        self.draw_ui(surface)
