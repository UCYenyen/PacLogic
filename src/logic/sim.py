import math
import random

from src.core import settings
from src.logic.grid import OPPOSITE, Level, bfs_dist, first_step, move
from src.logic.search import danger_map, plan

RUNNING = "running"
CAUGHT = "caught"
ESCAPED = "escaped"
BLOCKED = "blocked"


class PacManBrain:
    def __init__(self, level: Level, difficulty: str, pellet_mode: bool):
        self.level = level
        self.difficulty = difficulty
        self.config = settings.DIFFICULTIES[difficulty]
        self.pellet_mode = pellet_mode
        self.plans_made = 0
        self.nodes_expanded = 0
        self.last_ms = 0.0
        self.slowest_ms = 0.0
        result = self.make_plan(level.start, level.pellets)
        self.optimal_cost = result.cost or 0
        self.route = list(result.path or [])
        self.planned_route = list(self.route)

    def make_plan(self, position, pellets, blocked=frozenset(), danger=None):
        result = plan(self.level, position, pellets, self.pellet_mode, blocked, danger)
        self.plans_made += 1
        self.nodes_expanded += result.expanded
        self.last_ms = result.ms
        self.slowest_ms = max(self.slowest_ms, result.ms)
        return result

    def next_move(self, position, pellets, ghosts) -> str | None:
        if self.config["replan"]:
            danger = danger_map(self.level, ghosts)
            result = self.make_plan(position, pellets, frozenset(ghosts), danger)
            if result.path is None:
                result = self.make_plan(position, pellets, frozenset(), danger)
            self.route = list(result.path or [])
        if not self.route:
            return None
        return self.route.pop(0)

    def future_tiles(self, position) -> list:
        return tiles_along(position, self.route)


def tiles_along(start, directions) -> list:
    tiles = []
    position = start
    for direction in directions:
        position = move(position, direction)
        tiles.append(position)
    return tiles


def idle(sim, index):
    while True:
        yield None


class Sim:
    def __init__(self, level: Level, difficulty: str, pellet_mode: bool, ghost_count: int, controllers=()):
        self.level = level
        self.difficulty = difficulty
        self.pellet_mode = pellet_mode
        self.brain = PacManBrain(level, difficulty, pellet_mode)
        count = max(1, min(ghost_count, len(level.ghosts)))
        self.pac = level.start
        self.pac_dir = settings.PAC_START_DIRECTION
        self.ghosts = list(level.ghosts[:count])
        self.facing = [settings.GHOST_START_DIRECTION] * count
        self.pellets = level.pellets if pellet_mode else frozenset()
        self.tick = 0
        self.tick_cap = settings.TICK_CAP_FACTOR * self.brain.optimal_cost + settings.TICK_CAP_BONUS
        self.status = RUNNING
        self.previous_pac = self.pac
        self.previous_ghosts = list(self.ghosts)
        factories = list(controllers)[:count]
        factories += [idle] * (count - len(factories))
        self.controllers = [factory(self, index) for index, factory in enumerate(factories)]

    def ghost_can_enter(self, tile) -> bool:
        return self.level.passable(tile) and tile not in self.level.safe_zone

    def step(self):
        if self.status != RUNNING:
            return
        self.previous_pac = self.pac
        self.previous_ghosts = list(self.ghosts)
        for index, controller in enumerate(self.controllers):
            direction = next(controller)
            if direction is None:
                continue
            self.facing[index] = direction
            target = move(self.ghosts[index], direction)
            if self.ghost_can_enter(target):
                self.ghosts[index] = target
        pac_move = self.brain.next_move(self.pac, self.pellets, tuple(self.ghosts))
        if pac_move is not None:
            self.pac_dir = pac_move
            target = move(self.pac, pac_move)
            if self.level.passable(target):
                self.pac = target
        self.tick += 1
        if self.is_caught():
            self.status = CAUGHT
            return
        if self.pac in self.pellets:
            self.pellets = self.pellets - {self.pac}
        if self.pac == self.level.goal and not self.pellets:
            self.status = ESCAPED
        elif self.tick >= self.tick_cap:
            self.status = BLOCKED

    def is_caught(self) -> bool:
        for ghost, previous in zip(self.ghosts, self.previous_ghosts):
            if ghost == self.pac:
                return True
            if ghost == self.previous_pac and previous == self.pac:
                return True
        return False

    def run(self, max_ticks: int | None = None) -> str:
        limit = max_ticks if max_ticks is not None else self.tick_cap + 1
        while self.status == RUNNING and self.tick < limit:
            self.step()
        return self.status


def score_breakdown(sim: Sim, seconds_left: float) -> list:
    table = settings.SCORE
    if sim.status == CAUGHT:
        whole_seconds = max(0, int(seconds_left))
        ticks_left = max(0, sim.tick_cap - sim.tick)
        return [
            ("Catch", table["catch"]),
            (f"Planning time left ({whole_seconds} s)", whole_seconds * table["per_second_left"]),
            (f"Ticks left ({ticks_left})", ticks_left * table["per_tick_left"]),
        ]
    if sim.status == BLOCKED:
        return [("Blocked", table["blocked"])]
    if sim.status == ESCAPED:
        return [("Escaped", table["escaped"])]
    return []


def total_score(breakdown: list) -> int:
    return sum(points for _, points in breakdown)


def _ghost_options(sim: Sim, position) -> list:
    return [(name, tile) for name, tile in sim.level.neighbors(position) if tile not in sim.level.safe_zone]


def make_random_walker(seed: int):
    def random_walker(sim, index):
        rng = random.Random(seed * 31 + index)
        while True:
            options = _ghost_options(sim, sim.ghosts[index])
            yield rng.choice(options)[0] if options else None

    return random_walker


def chaser(sim, index):
    while True:
        yield first_step(sim.level, sim.ghosts[index], sim.pac, sim.level.safe_zone)


def _arcade_target(sim: Sim, index: int):
    if index % 2 == 0:
        return sim.pac
    target = sim.pac
    for _ in range(settings.ARCADE_LOOKAHEAD):
        target = move(target, sim.pac_dir)
    return target


def arcade(sim, index):
    while True:
        position = sim.ghosts[index]
        options = _ghost_options(sim, position)
        forward = [option for option in options if option[0] != OPPOSITE[sim.facing[index]]]
        choices = forward or options
        if not choices:
            yield None
            continue
        target = _arcade_target(sim, index)
        best = min(choices, key=lambda option: math.dist(option[1], target))
        yield best[0]


def oracle(sim, index):
    while True:
        position = sim.ghosts[index]
        reach = bfs_dist(sim.level, position, sim.level.safe_zone)
        target = sim.pac
        for ticks_ahead, tile in enumerate(sim.brain.future_tiles(sim.pac), start=1):
            if tile in reach and reach[tile] <= ticks_ahead:
                target = tile
                break
        if target == position:
            yield None
        else:
            yield first_step(sim.level, position, target, sim.level.safe_zone)
