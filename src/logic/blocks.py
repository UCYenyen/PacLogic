from src.core import settings
from src.logic.sim import idle

MOVE = "MOVE"
REPEAT = "REPEAT"
END = "END"

DIRECTION_WORDS = {"U": "UP", "R": "RIGHT", "D": "DOWN", "L": "LEFT"}

PALETTE = (
    {"type": MOVE, "dir": "U"},
    {"type": MOVE, "dir": "R"},
    {"type": MOVE, "dir": "D"},
    {"type": MOVE, "dir": "L"},
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


def block_text(block: dict) -> str:
    kind = block["type"]
    if kind == MOVE:
        return f"MOVE {DIRECTION_WORDS[block['dir']]}"
    if kind == REPEAT:
        return f"REPEAT {block['n']}x"
    if kind == END:
        return "_" * 10
    return kind


def cycle_value(block: dict) -> dict:
    if block["type"] != REPEAT:
        return block
    span = settings.REPEAT_MAX - settings.REPEAT_MIN + 1
    return {**block, "n": settings.REPEAT_MIN + (block["n"] - settings.REPEAT_MIN + 1) % span}


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
        elif kind == REPEAT:
            for _ in range(node["n"]):
                yield from _execute(node["body"], ops)


def run(tree: list, sim, ghost_index: int):
    yield from _execute(tree, [0])
    yield from idle(sim, ghost_index)
