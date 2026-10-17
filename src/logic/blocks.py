from src.core import settings
from src.logic.sim import idle

MOVE = "MOVE"
WAIT = "WAIT"
REPEAT = "REPEAT"
END = "END"

PALETTE = (
    {"type": MOVE, "dir": "U"},
    {"type": MOVE, "dir": "R"},
    {"type": MOVE, "dir": "D"},
    {"type": MOVE, "dir": "L"},
    {"type": WAIT, "n": settings.WAIT_MIN},
    {"type": REPEAT, "n": settings.REPEAT_MIN},
)


def new_blocks(template: dict) -> list:
    if template["type"] == REPEAT:
        return [dict(template), {"type": END}]
    return [dict(template)]


def count(program: list) -> int:
    return sum(1 for block in program if block["type"] != END)


def can_add(program: list, limit: int) -> bool:
    return count(program) < limit


def block_span(program: list, index: int) -> tuple[int, int]:
    kind = program[index]["type"]
    if kind not in (REPEAT, END):
        return index, index + 1
    forward = kind == REPEAT
    depth = 0
    position = index
    while 0 <= position < len(program):
        current = program[position]["type"]
        if current == REPEAT:
            depth += 1 if forward else -1
        elif current == END:
            depth += -1 if forward else 1
        if depth == 0:
            break
        position += 1 if forward else -1
    position = max(0, min(position, len(program) - 1))
    return (index, position + 1) if forward else (position, index + 1)


def depths(program: list) -> list:
    result = []
    depth = 0
    for block in program:
        if block["type"] == END:
            depth = max(0, depth - 1)
        result.append(depth)
        if block["type"] == REPEAT:
            depth += 1
    return result


COUNT_RANGES = {
    REPEAT: (settings.REPEAT_MIN, settings.REPEAT_MAX),
    WAIT: (settings.WAIT_MIN, settings.WAIT_MAX),
}


def cycle_value(block: dict) -> dict:
    if block["type"] not in COUNT_RANGES:
        return block
    low, high = COUNT_RANGES[block["type"]]
    return {**block, "n": low + (block["n"] - low + 1) % (high - low + 1)}


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, int(value)))


def parse(program: list) -> list:
    root = []
    current = root
    parents = []
    for block in program:
        kind = block["type"]
        if kind == MOVE:
            current.append({"type": MOVE, "dir": block["dir"]})
        elif kind == WAIT:
            current.append({"type": WAIT, "n": _clamp(block["n"], settings.WAIT_MIN, settings.WAIT_MAX)})
        elif kind == REPEAT:
            node = {"type": REPEAT, "n": _clamp(block["n"], settings.REPEAT_MIN, settings.REPEAT_MAX), "body": []}
            current.append(node)
            parents.append(current)
            current = node["body"]
        elif kind == END and parents:
            current = parents.pop()
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
