from functools import lru_cache

import pygame

from src.core import settings
from src.entities.enemy import Enemy, ghost_art_folders
from src.entities.player import Player
from src.logic.grid import Level
from src.ui.map_view import MapView


@lru_cache(maxsize=None)
def _report_missing_ghost_art(missing: tuple):
    print(f"[board] No ghost art yet for: {', '.join(missing)}. Reusing existing ghost art.")


class Board:
    def __init__(self, level: Level, area, ghost_count: int):
        self.level = level
        self.map_view = MapView(level, area)
        self.player = Player(self.map_view.scale)
        folders, missing = ghost_art_folders(ghost_count)
        if missing:
            _report_missing_ghost_art(tuple(missing))
        self.ghosts = [Enemy(folder, self.map_view.scale) for folder in folders]
        self.show_start()

    def show_start(self):
        start = self.level.start
        self.player.follow(start, start, settings.PAC_START_DIRECTION, 1.0, self.map_view)
        for index, ghost in enumerate(self.ghosts):
            tile = self.level.ghosts[index]
            ghost.follow(tile, tile, settings.GHOST_START_DIRECTION, 1.0, self.map_view)

    def show_sim(self, sim, progress: float):
        self.player.follow(sim.previous_pac, sim.pac, sim.pac_dir, progress, self.map_view)
        for index, ghost in enumerate(self.ghosts):
            ghost.follow(sim.previous_ghosts[index], sim.ghosts[index], sim.facing[index], progress, self.map_view)

    def select_ghost(self, selected_index: int | None):
        for index, ghost in enumerate(self.ghosts):
            ghost.selected = index == selected_index

    def ghost_at(self, position) -> int | None:
        tile = self.map_view.tile_at(position)
        for index in range(len(self.ghosts)):
            if self.level.ghosts[index] == tile:
                return index
        return None

    def update(self, dt: float):
        self.player.update(dt)
        for ghost in self.ghosts:
            ghost.update(dt)

    def draw(self, surface: pygame.Surface, pellets=(), route_tiles=(), goto_targets=()):
        self.map_view.draw(surface, pellets, route_tiles, goto_targets)
        for ghost in self.ghosts:
            surface.blit(ghost.image, ghost.rect)
        surface.blit(self.player.image, self.player.rect)
