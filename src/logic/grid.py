import random
from collections import deque
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from src.core import settings

DIRECTION_VECTORS = {"U": (0, -1), "R": (1, 0), "D": (0, 1), "L": (-1, 0)}
ORDERED_DIRECTIONS = tuple((name, DIRECTION_VECTORS[name]) for name in settings.MOVE_ORDER)
OPPOSITE = {"U": "D", "D": "U", "L": "R", "R": "L"}

WALL = "#"
FLOOR = "."
START = "P"
GOAL = "E"
GHOST = "G"
PELLET = "o"
LEGEND = {WALL, FLOOR, START, GOAL, GHOST, PELLET}


class LevelError(ValueError):
    pass


def step(position: tuple[int, int], direction: str) -> tuple[int, int]:
    dx, dy = DIRECTION_VECTORS[direction]
    return position[0] + dx, position[1] + dy


def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


@dataclass(frozen=True)
class Level:
    name: str
    width: int
    height: int
    walls: frozenset
    start: tuple[int, int]
    goal: tuple[int, int]
    ghosts: tuple
    pellets: frozenset

    def in_bounds(self, position: tuple[int, int]) -> bool:
        return 0 <= position[0] < self.width and 0 <= position[1] < self.height

    def passable(self, position: tuple[int, int]) -> bool:
        return self.in_bounds(position) and position not in self.walls

    def neighbors(self, position: tuple[int, int]):
        x, y = position
        for name, (dx, dy) in ORDERED_DIRECTIONS:
            tile = (x + dx, y + dy)
            if self.passable(tile):
                yield name, tile

    @cached_property
    def floor_tiles(self) -> tuple:
        return tuple(
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in self.walls
        )

    @cached_property
    def adjacency(self) -> dict:
        return {tile: tuple(self.neighbors(tile)) for tile in self.floor_tiles}

    @cached_property
    def safe_zone(self) -> frozenset:
        distances = bfs_dist(self, self.goal)
        return frozenset(tile for tile, distance in distances.items() if distance <= settings.SAFE_RADIUS)

    def to_text(self) -> str:
        rows = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                tile = (x, y)
                if tile in self.walls:
                    row.append(WALL)
                elif tile == self.start:
                    row.append(START)
                elif tile == self.goal:
                    row.append(GOAL)
                elif tile in self.ghosts:
                    row.append(GHOST)
                elif tile in self.pellets:
                    row.append(PELLET)
                else:
                    row.append(FLOOR)
            rows.append("".join(row))
        return "\n".join(rows)


def bfs_dist(level: Level, source: tuple[int, int], blocked: frozenset = frozenset()) -> dict:
    if not level.passable(source) or source in blocked:
        return {}
    distances = {source: 0}
    queue = deque([source])
    while queue:
        current = queue.popleft()
        next_distance = distances[current] + 1
        for _, tile in level.neighbors(current):
            if tile not in distances and tile not in blocked:
                distances[tile] = next_distance
                queue.append(tile)
    return distances


def first_step(level: Level, source: tuple[int, int], target: tuple[int, int], blocked: frozenset = frozenset()) -> str | None:
    if source == target:
        return None
    distances = bfs_dist(level, target, blocked)
    if source not in distances:
        return None
    wanted = distances[source] - 1
    for name, tile in level.neighbors(source):
        if distances.get(tile) == wanted:
            return name
    return None


def parse_level(text: str, name: str = "level") -> Level:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise LevelError(f"{name}: level is empty")
    width = max(len(line) for line in lines)
    height = len(lines)
    walls = set()
    starts = []
    goals = []
    ghosts = []
    pellets = set()
    for y, line in enumerate(lines):
        for x in range(width):
            character = line[x] if x < len(line) else WALL
            if character not in LEGEND:
                raise LevelError(f"{name}: unknown character {character!r} at {(x, y)}")
            tile = (x, y)
            if character == WALL:
                walls.add(tile)
            elif character == START:
                starts.append(tile)
            elif character == GOAL:
                goals.append(tile)
            elif character == GHOST:
                ghosts.append(tile)
            elif character == PELLET:
                pellets.add(tile)
    if len(starts) != 1:
        raise LevelError(f"{name}: needs exactly one {START}, found {len(starts)}")
    if len(goals) != 1:
        raise LevelError(f"{name}: needs exactly one {GOAL}, found {len(goals)}")
    return Level(
        name=name,
        width=width,
        height=height,
        walls=frozenset(walls),
        start=starts[0],
        goal=goals[0],
        ghosts=tuple(ghosts),
        pellets=frozenset(pellets),
    )


def validate_level(level: Level) -> Level:
    if not 1 <= len(level.ghosts) <= settings.MAX_GHOSTS:
        raise LevelError(f"{level.name}: needs 1 to {settings.MAX_GHOSTS} ghosts, found {len(level.ghosts)}")
    if len(level.pellets) > settings.MAX_PELLETS:
        raise LevelError(f"{level.name}: at most {settings.MAX_PELLETS} pellets, found {len(level.pellets)}")
    reachable = bfs_dist(level, level.start)
    unreachable = [tile for tile in level.floor_tiles if tile not in reachable]
    if unreachable:
        raise LevelError(f"{level.name}: tiles not reachable from {START}: {unreachable[:5]}")
    inside = [ghost for ghost in level.ghosts if ghost in level.safe_zone]
    if inside:
        raise LevelError(f"{level.name}: ghosts start inside the safe zone: {inside}")
    return level


def load_level(path: Path) -> Level:
    level = parse_level(Path(path).read_text(), Path(path).stem)
    return validate_level(level)


def _carve_maze(width: int, height: int, rng: random.Random) -> set:
    cells = [(x, y) for y in range(1, height - 1, 2) for x in range(1, width - 1, 2)]
    cell_set = set(cells)
    first = rng.choice(cells)
    floor = {first}
    visited = {first}
    stack = [first]
    while stack:
        x, y = stack[-1]
        options = [
            (x + dx, y + dy)
            for dx, dy in ((0, -2), (2, 0), (0, 2), (-2, 0))
            if (x + dx, y + dy) in cell_set and (x + dx, y + dy) not in visited
        ]
        if not options:
            stack.pop()
            continue
        nx, ny = rng.choice(options)
        floor.add(((x + nx) // 2, (y + ny) // 2))
        floor.add((nx, ny))
        visited.add((nx, ny))
        stack.append((nx, ny))
    for x, y in cells:
        open_sides = sum(1 for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)) if (x + dx, y + dy) in floor)
        if open_sides != 1 or rng.random() >= settings.BRAID_CHANCE:
            continue
        closed = [
            ((x + dx // 2, y + dy // 2))
            for dx, dy in ((0, -2), (2, 0), (0, 2), (-2, 0))
            if (x + dx, y + dy) in cell_set and (x + dx // 2, y + dy // 2) not in floor
        ]
        if closed:
            floor.add(rng.choice(closed))
    return floor


def _farthest(distances: dict) -> tuple[int, int]:
    return max(distances, key=lambda tile: (distances[tile], -tile[1], -tile[0]))


def _route_tiles(level: Level, stops: list) -> set:
    tables = {stop: bfs_dist(level, stop) for stop in stops}
    tiles = set()
    for index, a in enumerate(stops):
        for b in stops[index + 1:]:
            length = tables[a][b]
            tiles.update(tile for tile in level.floor_tiles if tables[a][tile] + tables[b][tile] == length)
    return tiles


def _pick_ghosts(level: Level, count: int, rng: random.Random) -> list:
    from_start = bfs_dist(level, level.start)
    on_route = _route_tiles(level, [level.start, level.goal, *sorted(level.pellets)])
    open_tiles = [tile for tile in level.floor_tiles if tile not in level.safe_zone and tile not in on_route]
    candidates = [tile for tile in open_tiles if from_start[tile] >= settings.GHOST_MIN_START_DISTANCE]
    if len(candidates) < count:
        candidates = open_tiles
    if len(candidates) < count:
        candidates = [tile for tile in level.floor_tiles if tile not in level.safe_zone and tile != level.start]
    rng.shuffle(candidates)
    chosen = []
    for spacing in (6, 4, 2, 0):
        for tile in candidates:
            if len(chosen) == count:
                break
            if tile not in chosen and all(manhattan(tile, other) >= spacing for other in chosen):
                chosen.append(tile)
        if len(chosen) == count:
            break
    return sorted(chosen, key=lambda tile: (tile[1], tile[0]))


def generate_level(width: int, height: int, seed: int, pellet_count: int, ghost_count: int = settings.MAX_GHOSTS) -> Level:
    rng = random.Random(seed)
    floor = _carve_maze(width, height, rng)
    walls = frozenset((x, y) for y in range(height) for x in range(width) if (x, y) not in floor)
    name = f"random {width}x{height} #{seed}"
    draft = Level(name, width, height, walls, min(floor), min(floor), (), frozenset())
    goal = _farthest(bfs_dist(draft, draft.start))
    start = _farthest(bfs_dist(draft, goal))
    draft = Level(name, width, height, walls, start, goal, (), frozenset())
    free = [tile for tile in draft.floor_tiles if tile not in draft.safe_zone and tile != start]
    pellets = frozenset(rng.sample(free, min(pellet_count, len(free))))
    draft = Level(name, width, height, walls, start, goal, (), pellets)
    ghosts = _pick_ghosts(draft, ghost_count, rng)
    level = Level(name, width, height, walls, start, goal, tuple(ghosts), pellets)
    return validate_level(level)
