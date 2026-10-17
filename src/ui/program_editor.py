import math
from dataclasses import dataclass

import pygame

from src.core import settings
from src.logic import blocks
from src.ui.block_view import block_size, draw_block
from src.ui.label import FlashMessage, Label
from src.ui.panel import Panel

PALETTE = "palette"
PROGRAM = "program"


@dataclass
class Press:
    source: str
    index: int
    start: tuple[int, int]


class ProgramEditor:
    def __init__(self, limit: int, flash: FlashMessage):
        self.limit = limit
        self.flash = flash
        self.program = []
        self.press = None
        self.dragging = False
        self.editing = None
        self.scroll = 0
        self.palette_rect = pygame.Rect(settings.PALETTE_RECT)
        self.program_rect = pygame.Rect(settings.PROGRAM_RECT)
        self.block_width, self.block_height = block_size()
        self.palette_rects = [
            pygame.Rect(
                self.palette_rect.x + settings.PANEL_PADDING,
                self.palette_rect.y + settings.PANEL_PADDING + index * (self.block_height + settings.BLOCK_GAP),
                self.block_width,
                self.block_height,
            )
            for index in range(len(blocks.PALETTE))
        ]
        self.header = Label("", (self.palette_rect.x, settings.PLAN_TITLE_Y), settings.FONT_MEDIUM, settings.ACCENT_COLOR, "midleft")
        self.counter = Label("", (self.program_rect.right, settings.PLAN_TITLE_Y), settings.FONT_MEDIUM, anchor="midright")
        self.ui = [
            Panel(self.palette_rect),
            Panel(self.program_rect),
            self.header,
            self.counter,
        ]

    def edit(self, ghost_index: int, program: list):
        self.program = program
        self.cancel()
        self.scroll = 0
        self.header.set_text(f"Ghost {ghost_index + 1}")

    def cancel(self):
        self.press = None
        self.dragging = False
        self.editing = None

    def palette_at(self, position) -> int | None:
        for index, rect in enumerate(self.palette_rects):
            if rect.collidepoint(position):
                return index
        return None

    def row_top(self, slot: int) -> int:
        return self.program_rect.y + settings.PANEL_PADDING + slot * settings.ROW_HEIGHT - self.scroll

    def row_at(self, position) -> int | None:
        if not self.program_rect.collidepoint(position):
            return None
        index = (position[1] - self.program_rect.y - settings.PANEL_PADDING + self.scroll) // settings.ROW_HEIGHT
        return index if 0 <= index < len(self.program) else None

    def insertion_index(self, position, length: int) -> int:
        offset = position[1] - self.program_rect.y - settings.PANEL_PADDING + self.scroll + settings.ROW_HEIGHT // 2
        return max(0, min(length, offset // settings.ROW_HEIGHT))

    def max_scroll(self) -> int:
        content = (len(self.program) + 1) * settings.ROW_HEIGHT + 2 * settings.PANEL_PADDING
        return max(0, content - self.program_rect.height)

    def depth_at(self, x: int, index: int) -> int:
        left = x - self.block_width // 2 - self.program_rect.x - settings.PANEL_PADDING
        lowest, highest = blocks.depth_range(self.program, index)
        return max(lowest, min(highest, round(left / settings.INDENT)))

    def insert(self, template: dict, index: int, depth: int):
        if not blocks.can_add(self.program, self.limit):
            self.flash.show(f"Block limit reached ({self.limit})")
            return
        self.program.insert(index, blocks.new_block(template, depth))

    def mouse_down(self, position) -> bool:
        self.editing = None
        palette_index = self.palette_at(position)
        if palette_index is not None:
            self.press = Press(PALETTE, palette_index, position)
            return True
        row = self.row_at(position)
        if row is not None:
            start, _ = blocks.block_span(self.program, row)
            self.press = Press(PROGRAM, start, position)
            return True
        return False

    def mouse_up(self, position):
        press = self.press
        dragging = self.dragging
        self.cancel()
        if press is None:
            return
        if dragging:
            self.drop(press, position)
        else:
            self.click(press)

    def click(self, press: Press):
        if press.source == PALETTE:
            end = len(self.program)
            self.insert(blocks.PALETTE[press.index], end, blocks.depth_range(self.program, end)[1])
        elif self.program[press.index]["type"] in blocks.COUNT_RANGES:
            self.start_typing(self.program[press.index])

    def start_typing(self, block: dict):
        self.editing = block
        low, high = blocks.COUNT_RANGES[block["type"]]
        self.flash.show(f"Type a number from {low} to {high}, then press Enter")

    def type_key(self, event: pygame.event.Event):
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.editing = None
            return
        if not event.unicode.isdigit():
            return
        value = int(event.unicode)
        if blocks.valid_count(self.editing["type"], value):
            self.editing["n"] = value
        else:
            low, high = blocks.COUNT_RANGES[self.editing["type"]]
            self.flash.show(f"{self.editing['type']} takes {low} to {high}")

    def drop(self, press: Press, position):
        inside = self.program_rect.collidepoint(position)
        if press.source == PALETTE:
            if inside:
                index = self.insertion_index(position, len(self.program))
                self.insert(blocks.PALETTE[press.index], index, self.depth_at(position[0], index))
            return
        start, stop = blocks.block_span(self.program, press.index)
        moved = self.program[start:stop]
        del self.program[start:stop]
        if inside:
            index = self.insertion_index(position, len(self.program))
            shift = self.depth_at(position[0], index) - moved[0]["depth"]
            self.program[index:index] = [{**block, "depth": block["depth"] + shift} for block in moved]

    def delete_row(self, position) -> bool:
        if self.press is not None:
            return False
        row = self.row_at(position)
        if row is None:
            return False
        start, stop = blocks.block_span(self.program, row)
        del self.program[start:stop]
        return True

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN and self.editing is not None:
            self.type_key(event)
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.mouse_down(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            return self.delete_row(event.pos)
        if event.type == pygame.MOUSEMOTION and self.press and not self.dragging:
            self.dragging = math.dist(self.press.start, event.pos) > settings.DRAG_THRESHOLD
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.mouse_up(event.pos)
        elif event.type == pygame.MOUSEWHEEL and self.program_rect.collidepoint(pygame.mouse.get_pos()):
            self.scroll = max(0, min(self.max_scroll(), self.scroll - event.y * settings.SCROLL_STEP))
        return False

    def update(self, dt: float):
        self.counter.set_text(f"Blocks {len(self.program)}/{self.limit}")

    def dragged_block(self) -> dict | None:
        if not self.dragging or self.press is None:
            return None
        if self.press.source == PALETTE:
            return blocks.PALETTE[self.press.index]
        return self.program[self.press.index]

    def draw_palette(self, surface: pygame.Surface):
        for template, rect in zip(blocks.PALETTE, self.palette_rects):
            draw_block(surface, template, rect.topleft)

    def draw_program(self, surface: pygame.Surface):
        hidden = range(0)
        if self.dragging and self.press.source == PROGRAM:
            hidden = range(*blocks.block_span(self.program, self.press.index))
        shown = [block for index, block in enumerate(self.program) if index not in hidden]
        mouse = pygame.mouse.get_pos()
        gap = self.insertion_index(mouse, len(shown)) if self.dragging and self.program_rect.collidepoint(mouse) else None
        surface.set_clip(self.program_rect.inflate(-4, -4))
        for index, block in enumerate(shown):
            slot = index + 1 if gap is not None and index >= gap else index
            top = self.row_top(slot)
            left = self.program_rect.x + settings.PANEL_PADDING + block["depth"] * settings.INDENT
            draw_block(surface, block, (left, top), block is self.editing)
        surface.set_clip(None)

    def draw(self, surface: pygame.Surface):
        for component in self.ui:
            component.draw(surface)
        self.draw_palette(surface)
        self.draw_program(surface)
        dragged = self.dragged_block()
        if dragged is not None:
            x, y = pygame.mouse.get_pos()
            draw_block(surface, dragged, (x - self.block_width // 2, y - self.block_height // 2))
