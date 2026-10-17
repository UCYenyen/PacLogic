from src.core import settings
from src.logic.sim import idle

MOVE = "MOVE"
WAIT = "WAIT"
REPEAT = "REPEAT"

PALETTE = (
    {"type": MOVE, "dir": "U"},
    {"type": MOVE, "dir": "R"},
    {"type": MOVE, "dir": "D"},
    {"type": MOVE, "dir": "L"},
    {"type": WAIT, "n": settings.WAIT_MIN},
    {"type": REPEAT, "n": settings.REPEAT_MIN},
)


def new_block(template: dict, depth: int) -> dict:
    return {**template, "depth": depth}


def can_add(program: list, limit: int) -> bool:
    return len(program) < limit


def block_span(program: list, index: int) -> tuple[int, int]:
    head = program[index]
    stop = index + 1
    if head["type"] == REPEAT:
        while stop < len(program) and program[stop]["depth"] > head["depth"]:
            stop += 1
    return index, stop


def depth_range(program: list, index: int) -> tuple[int, int]:
    previous = program[index - 1] if index > 0 else None
    highest = previous["depth"] + (previous["type"] == REPEAT) if previous else 0
    lowest = program[index]["depth"] if index < len(program) else 0
    return lowest, highest


COUNT_RANGES = {
    REPEAT: (settings.REPEAT_MIN, settings.REPEAT_MAX),
    WAIT: (settings.WAIT_MIN, settings.WAIT_MAX),
}


def valid_count(kind: str, value: int) -> bool:
    low, high = COUNT_RANGES[kind]
    return low <= value <= high


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, int(value)))


def parse(program: list) -> list:
    root = []
    levels = [root]
    for block in program:
        depth = max(0, min(block["depth"], len(levels) - 1))
        del levels[depth + 1:]
        kind = block["type"]
        if kind == MOVE:
            levels[depth].append({"type": MOVE, "dir": block["dir"]})
        elif kind == WAIT:
            levels[depth].append({"type": WAIT, "n": _clamp(block["n"], settings.WAIT_MIN, settings.WAIT_MAX)})
        elif kind == REPEAT:
            node = {"type": REPEAT, "n": _clamp(block["n"], settings.REPEAT_MIN, settings.REPEAT_MAX), "body": []}
            levels[depth].append(node)
            levels.append(node["body"])
    return root


def _execute(nodes: list, ops: list):
    for node in nodes:
        ops[0] += 1
        if ops[0] > settings.OP_CAP:
            ops[0] = 0
            yield None
        kind = node["type"]
        if kind == MOVE:
            ops[0] = 0
            yield node["dir"]
        elif kind == WAIT:
            ops[0] = 0
            for _ in range(node["n"]):
                yield None
        elif kind == REPEAT:
            for _ in range(node["n"]):
                yield from _execute(node["body"], ops)


def run(tree: list, sim, ghost_index: int):
    yield from _execute(tree, [0])
    yield from idle(sim, ghost_index)
