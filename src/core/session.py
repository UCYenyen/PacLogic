import random
from functools import lru_cache

from src.core import settings
from src.logic.grid import generate_level, load_level
from src.logic.sim import Sim, tiles_along

LEVEL_CHOICES = tuple(settings.LEVEL_FILES) + tuple(settings.RANDOM_LEVELS)
AI_CHOICES = tuple(settings.DIFFICULTIES)
OPTIONS = ("level", "ai", "ghosts", "mode", "time")


@lru_cache(maxsize=None)
def _handmade_ghost_count(file_name: str) -> int:
    return len(load_level(settings.LEVELS_DIR / file_name).ghosts)


class Session:
    def __init__(self):
        self.level_index = 0
        self.ai_index = 0
        self.ghost_count = 1
        self.mode_index = 0
        self.time_index = 0
        self.level = None
        self.seed = None
        self.route_tiles = []
        self.optimal_cost = 0
        self.tick_cap = 0
        self.programs = []
        self.trees = []
        self.seconds_left = 0.0

    @property
    def level_choice(self) -> str:
        return LEVEL_CHOICES[self.level_index]

    @property
    def difficulty(self) -> str:
        return AI_CHOICES[self.ai_index]

    @property
    def config(self) -> dict:
        return settings.DIFFICULTIES[self.difficulty]

    @property
    def pellet_mode(self) -> bool:
        return self.mode_index == 1

    @property
    def mode_name(self) -> str:
        return settings.WIN_MODES[self.mode_index]

    @property
    def planning_time(self) -> int:
        return settings.PLANNING_TIMES[self.time_index]

    def max_ghosts(self) -> int:
        if self.level_choice in settings.LEVEL_FILES:
            return _handmade_ghost_count(settings.LEVEL_FILES[self.level_choice])
        return settings.MAX_GHOSTS

    def cycle(self, option: str, delta: int):
        if option == "level":
            self.level_index = (self.level_index + delta) % len(LEVEL_CHOICES)
            self.ghost_count = min(self.ghost_count, self.max_ghosts())
        elif option == "ai":
            self.ai_index = (self.ai_index + delta) % len(AI_CHOICES)
        elif option == "ghosts":
            self.ghost_count = (self.ghost_count - 1 + delta) % self.max_ghosts() + 1
        elif option == "mode":
            self.mode_index = (self.mode_index + delta) % len(settings.WIN_MODES)
        elif option == "time":
            self.time_index = (self.time_index + delta) % len(settings.PLANNING_TIMES)

    def option_text(self, option: str) -> str:
        texts = {
            "level": f"Level: {self.level_choice}",
            "ai": f"Pac-Man AI: {self.difficulty}",
            "ghosts": f"Ghosts: {self.ghost_count}",
            "mode": f"Win mode: {self.mode_name}",
            "time": f"Planning time: {self.planning_time} s",
        }
        return texts[option]

    def prepare(self):
        if self.level_choice in settings.LEVEL_FILES:
            self.seed = None
            level = load_level(settings.LEVELS_DIR / settings.LEVEL_FILES[self.level_choice])
        else:
            width, height, pellets = settings.RANDOM_LEVELS[self.level_choice]
            self.seed = random.randrange(1_000_000)
            level = generate_level(width, height, self.seed, pellets)
        self.level = level
        self.ghost_count = min(self.ghost_count, len(level.ghosts))
        preview = self.new_sim()
        self.route_tiles = tiles_along(level.start, preview.brain.planned_route)
        self.optimal_cost = preview.brain.optimal_cost
        self.tick_cap = preview.tick_cap
        self.programs = [[] for _ in range(self.ghost_count)]
        self.trees = []

    def new_sim(self, controllers=()) -> Sim:
        return Sim(self.level, self.difficulty, self.pellet_mode, self.ghost_count, controllers)

    def start_pellets(self) -> frozenset:
        return self.level.pellets if self.pellet_mode else frozenset()
