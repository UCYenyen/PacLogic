from src.core import settings
from src.logic.grid import manhattan, move

MOVE = "MOVE"
WAIT = "WAIT"
REPEAT = "REPEAT"
END = "END"
IF = "IF"
ELSE = "ELSE"

WALL_AHEAD = "wall"
PAC_NEAR = "near"
PAC_IN_LINE = "line"

UNCOUNTED = {ELSE, END}
OPENERS = {REPEAT, IF}
DIRECTION_WORDS = {"U": "UP", "R": "RIGHT", "D": "DOWN", "L": "LEFT"}

PALETTE = (
    {"type": MOVE, "dir": "U"},
    {"type": MOVE, "dir": "R"},
    {"type": MOVE, "dir": "D"},
    {"type": MOVE, "dir": "L"},
    {"type": WAIT},
    {"type": REPEAT, "n": settings.REPEAT_MIN},
    {"type": END},
    {"type": IF, "cond": WALL_AHEAD},
    {"type": IF, "cond": PAC_NEAR, "n": 3},
    {"type": IF, "cond": PAC_IN_LINE},
    {"type": ELSE},
)


def new_block(template: dict) -> dict:
    return dict(template)


def count(program: list) -> int:
    return sum(1 for block in program if block["type"] not in UNCOUNTED)


def can_add(program: list, block: dict, limit: int) -> bool:
    return block["type"] in UNCOUNTED or count(program) < limit


def depths(program: list) -> list:
    result = []
    stack = []
    for block in program:
        kind = block["type"]
        if kind == END:
            if stack:
                stack.pop()
            result.append(len(stack))
        elif kind == ELSE:
            if stack and stack[-1] == IF:
                stack[-1] = ELSE
                result.append(len(stack) - 1)
            else:
                result.append(len(stack))
        else:
            result.append(len(stack))
            if kind in OPENERS:
                stack.append(kind)
    return result


def block_text(block: dict) -> str:
    kind = block["type"]
    if kind == MOVE:
        return f"MOVE {DIRECTION_WORDS[block['dir']]}"
    if kind == REPEAT:
        return f"REPEAT {block['n']}x"
    if kind == IF:
        if block["cond"] == WALL_AHEAD:
            return "IF WALL AHEAD"
        if block["cond"] == PAC_NEAR:
            return f"IF PAC WITHIN {block['n']}"
        return "IF PAC IN LINE"
    return kind


def cycle_value(block: dict) -> dict:
    if block["type"] == REPEAT:
        span = settings.REPEAT_MAX - settings.REPEAT_MIN + 1
        return {**block, "n": settings.REPEAT_MIN + (block["n"] - settings.REPEAT_MIN + 1) % span}
    if block["type"] == IF and block["cond"] == PAC_NEAR:
        span = settings.NEAR_MAX - settings.NEAR_MIN + 1
        return {**block, "n": settings.NEAR_MIN + (block["n"] - settings.NEAR_MIN + 1) % span}
    return block


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, int(value)))


def parse(program: list) -> list:
    root = []
    current = root
    stack = []
    for block in program:
        kind = block["type"]
        if kind == MOVE:
            current.append({"type": MOVE, "dir": block["dir"]})
        elif kind == WAIT:
            current.append({"type": WAIT})
        elif kind == REPEAT:
            node = {"type": REPEAT, "n": _clamp(block["n"], settings.REPEAT_MIN, settings.REPEAT_MAX), "body": []}
            current.append(node)
            stack.append([node, current, False])
            current = node["body"]
        elif kind == IF:
            node = {"type": IF, "cond": block["cond"], "n": block.get("n", 0), "then": [], "else": []}
            current.append(node)
            stack.append([node, current, False])
            current = node["then"]
        elif kind == ELSE:
            if stack and stack[-1][0]["type"] == IF and not stack[-1][2]:
                stack[-1][2] = True
                current = stack[-1][0]["else"]
        elif kind == END:
            if stack:
                _, parent, _ = stack.pop()
                current = parent
    return root


def condition_holds(node: dict, sim, ghost_index: int) -> bool:
    ghost = sim.ghosts[ghost_index]
    if node["cond"] == WALL_AHEAD:
        return not sim.level.passable(move(ghost, sim.facing[ghost_index]))
    if node["cond"] == PAC_NEAR:
        return manhattan(ghost, sim.pac) <= node["n"]
    if node["cond"] == PAC_IN_LINE:
        return ghost[0] == sim.pac[0] or ghost[1] == sim.pac[1]
    return False


def _execute(nodes: list, sim, ghost_index: int, ops: list):
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
            yield None
        elif kind == REPEAT:
            for _ in range(node["n"]):
                yield from _execute(node["body"], sim, ghost_index, ops)
        elif kind == IF:
            branch = node["then"] if condition_holds(node, sim, ghost_index) else node["else"]
            yield from _execute(branch, sim, ghost_index, ops)


def run(tree: list, sim, ghost_index: int):
    ops = [0]
    while True:
        yield from _execute(tree, sim, ghost_index, ops)
        ops[0] += 1
        if ops[0] > settings.OP_CAP:
            ops[0] = 0
            yield None
