import heapq
import time
from collections import deque
from dataclasses import dataclass
from functools import lru_cache

from src.core import settings
from src.logic.grid import Level, bfs_dist, manhattan, move

ASTAR = "astar"
UCS = "ucs"
GREEDY = "greedy"


@dataclass
class SearchResult:
    path: list | None
    cost: int | None
    expanded: int
    max_frontier: int
    ms: float


def _elapsed_ms(started: float) -> float:
    return (time.perf_counter() - started) * 1000.0


def _rebuild(parents: dict, state) -> list:
    path = []
    while parents[state] is not None:
        state, direction = parents[state]
        path.append(direction)
    path.reverse()
    return path


def best_first(start, is_goal, successors, h, g_weight: float = 1) -> SearchResult:
    started = time.perf_counter()
    start_h = h(start)
    frontier = [(start_h, start_h, 0, start)]
    best_g = {start: 0}
    parents = {start: None}
    closed = set()
    counter = 0
    expanded = 0
    max_frontier = 1
    while frontier:
        _, _, _, state = heapq.heappop(frontier)
        if state in closed:
            continue
        if is_goal(state):
            return SearchResult(_rebuild(parents, state), best_g[state], expanded, max_frontier, _elapsed_ms(started))
        closed.add(state)
        expanded += 1
        state_g = best_g[state]
        for direction, next_state, step_cost in successors(state):
            if next_state in closed:
                continue
            next_g = state_g + step_cost
            if next_state not in best_g or next_g < best_g[next_state]:
                best_g[next_state] = next_g
                parents[next_state] = (state, direction)
                next_h = h(next_state)
                counter += 1
                heapq.heappush(frontier, (g_weight * next_g + next_h, next_h, counter, next_state))
        if len(frontier) > max_frontier:
            max_frontier = len(frontier)
    return SearchResult(None, None, expanded, max_frontier, _elapsed_ms(started))


def breadth_first(start, is_goal, successors) -> SearchResult:
    started = time.perf_counter()
    parents = {start: None}
    queue = deque([start])
    expanded = 0
    max_frontier = 1
    while queue:
        state = queue.popleft()
        if is_goal(state):
            path = _rebuild(parents, state)
            return SearchResult(path, len(path), expanded, max_frontier, _elapsed_ms(started))
        expanded += 1
        for direction, next_state, _ in successors(state):
            if next_state not in parents:
                parents[next_state] = (state, direction)
                queue.append(next_state)
        if len(queue) > max_frontier:
            max_frontier = len(queue)
    return SearchResult(None, None, expanded, max_frontier, _elapsed_ms(started))


def make_successors(level: Level, blocked: frozenset = frozenset(), danger: dict | None = None):
    adjacency = level.adjacency
    penalties = danger or {}

    def successors(state):
        position, pellets = state
        for direction, tile in adjacency[position]:
            if tile in blocked:
                continue
            remaining = pellets - {tile} if tile in pellets else pellets
            yield direction, (tile, remaining), 1 + penalties.get(tile, 0)

    return successors


def make_goal_test(level: Level):
    goal = level.goal

    def is_goal(state):
        return state[0] == goal and not state[1]

    return is_goal


@lru_cache(maxsize=None)
def distance_table(level: Level, source: tuple[int, int]) -> dict:
    return bfs_dist(level, source)


def zero_heuristic(state) -> int:
    return 0


def manhattan_heuristic(level: Level):
    goal = level.goal

    def h(state):
        position, pellets = state
        best = manhattan(position, goal)
        for pellet in pellets:
            distance = manhattan(position, pellet)
            if distance > best:
                best = distance
        return best

    return h


def maze_heuristic(level: Level):
    to_goal = distance_table(level, level.goal)
    pellet_tables = {pellet: distance_table(level, pellet) for pellet in level.pellets}
    memo = {}

    def h(state):
        if state in memo:
            return memo[state]
        position, pellets = state
        best = to_goal[position]
        for pellet in pellets:
            distance = pellet_tables[pellet][position] + to_goal[pellet]
            if distance > best:
                best = distance
        memo[state] = best
        return best

    return h


def heuristic_for(level: Level, pellet_mode: bool):
    return maze_heuristic(level) if pellet_mode else manhattan_heuristic(level)


def route_costs(level: Level, position, pellets, pellet_mode: bool, directions, start_g: int = 0) -> list:
    h = heuristic_for(level, pellet_mode)
    remaining = frozenset(pellets) if pellet_mode else frozenset()
    costs = []
    for g, direction in enumerate(directions, start=start_g + 1):
        position = move(position, direction)
        remaining = remaining - {position}
        costs.append((position, g, h((position, remaining))))
    return costs


def danger_map(level: Level, ghosts) -> dict:
    danger = {}
    radius = settings.DANGER_RADIUS
    for gx, gy in ghosts:
        for dy in range(-radius, radius + 1):
            span = radius - abs(dy)
            for dx in range(-span, span + 1):
                tile = (gx + dx, gy + dy)
                if level.passable(tile):
                    danger[tile] = settings.DANGER_PENALTY
    return danger


def plan(
    level: Level,
    position: tuple[int, int],
    pellets: frozenset,
    pellet_mode: bool,
    blocked: frozenset = frozenset(),
    danger: dict | None = None,
    algorithm: str = ASTAR,
) -> SearchResult:
    start = (position, frozenset(pellets) if pellet_mode else frozenset())
    successors = make_successors(level, blocked, danger)
    is_goal = make_goal_test(level)
    heuristic = heuristic_for(level, pellet_mode)
    if algorithm == UCS:
        return best_first(start, is_goal, successors, zero_heuristic)
    if algorithm == GREEDY:
        return best_first(start, is_goal, successors, heuristic, g_weight=0)
    return best_first(start, is_goal, successors, heuristic)


def plan_bfs(level: Level, position: tuple[int, int], pellets: frozenset, pellet_mode: bool) -> SearchResult:
    start = (position, frozenset(pellets) if pellet_mode else frozenset())
    return breadth_first(start, make_goal_test(level), make_successors(level))
