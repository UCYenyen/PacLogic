import math

import pygame

from src.core import settings
from src.logic import blocks
from src.scenes import play_scene
from src.scenes.base_scene import BaseScene
from src.ui.block_view import block_size, draw_block
from src.ui.board import Board
from src.ui.button import ImageButton
from src.ui.label import FlashMessage, Label
from src.ui.panel import Panel

PALETTE = "palette"
PROGRAM = "program"


class PlanScene(BaseScene):
    def __init__(self, game, session):
        super().__init__(game)
        self.session = session
        self.board = Board(session.level, settings.PLAN_MAP_RECT, session.ghost_count)
        self.programs = session.programs
        self.limit = session.config["block_limit"]
        self.time_left = float(session.planning_time)
        self.selected_ghost = None
        self.armed_goto = None
        self.press = None
        self.dragging = False
        self.scroll = 0
        self.cancel_key = pygame.key.key_code(settings.KEY_CANCEL)
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
        map_center_x = pygame.Rect(settings.PLAN_MAP_RECT).centerx
        self.palette_panel = Panel(self.palette_rect)
        self.program_panel = Panel(self.program_rect)
        self.timer = Label("", (map_center_x, 36), settings.FONT_LARGE, anchor="center")
        self.header = Label("", (self.palette_rect.x, 28), settings.FONT_MEDIUM, settings.ACCENT_COLOR)
        self.counter = Label("", (self.program_rect.right, 28), settings.FONT_MEDIUM, anchor="topright")
        self.hint = Label(
            "Click a ghost to program it",
            ((self.palette_rect.x + self.program_rect.right) // 2, self.program_rect.centery),
            settings.FONT_MEDIUM,
            settings.TEXT_DIM_COLOR,
            "center",
        )
        self.goto_hint = Label(
            "Click a map tile to set the GOTO target (Esc cancels)",
            (map_center_x, 690),
            settings.FONT_SMALL,
            settings.ACCENT_COLOR,
            "center",
        )
        self.flash = FlashMessage((760, 672), settings.FONT_SMALL)
        self.lock_button = ImageButton((self.program_rect.centerx, 672), self.lock, "Lock & Run")
        self.ui = [
            self.timer,
            self.header,
            self.counter,
            self.palette_panel,
            self.program_panel,
            self.hint,
            self.goto_hint,
            self.lock_button,
            self.flash,
        ]
        self.refresh_labels()

    @property
    def current_program(self) -> list:
        return self.programs[self.selected_ghost]

    def select_ghost(self, index: int):
        self.selected_ghost = index
        self.armed_goto = None
        self.scroll = 0
        self.board.select_ghost(index)
        self.refresh_labels()

    def refresh_labels(self):
        editing = self.selected_ghost is not None
        for component in (self.header, self.counter, self.palette_panel, self.program_panel):
            component.visible = editing
        self.hint.visible = not editing
        self.goto_hint.visible = self.armed_goto is not None
        seconds = max(0, math.ceil(self.time_left))
        color = settings.WARNING_COLOR if self.time_left < settings.TIMER_WARNING_SECONDS else settings.TEXT_COLOR
        self.timer.set_text(f"{seconds // 60}:{seconds % 60:02d}", color)
        if editing:
            self.header.set_text(f"Ghost {self.selected_ghost + 1}")
            self.counter.set_text(f"Blocks {blocks.count(self.current_program)}/{self.limit}")

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
        return index if 0 <= index < len(self.current_program) else None

    def insertion_index(self, position, length: int) -> int:
        offset = position[1] - self.program_rect.y - settings.PANEL_PADDING + self.scroll + settings.ROW_HEIGHT // 2
        return max(0, min(length, offset // settings.ROW_HEIGHT))

    def max_scroll(self) -> int:
        content = (len(self.current_program) + 1) * settings.ROW_HEIGHT + 2 * settings.PANEL_PADDING
        return max(0, content - self.program_rect.height)

    def insert(self, block: dict, index: int) -> bool:
        program = self.current_program
        if block["type"] not in blocks.UNCOUNTED and blocks.count(program) >= self.limit:
            self.flash.show(f"Block limit reached ({self.limit})")
            return False
        program.insert(index, block)
        return True

    def set_goto_target(self, tile):
        level = self.session.level
        if tile in level.walls:
            self.flash.show("A GOTO target can't be a wall")
        elif tile in level.safe_zone:
            self.flash.show("A GOTO target can't be in the safe zone")
        else:
            self.armed_goto["target"] = tile
            self.armed_goto = None

    def mouse_down(self, position):
        if self.selected_ghost is not None:
            palette_index = self.palette_at(position)
            if palette_index is not None:
                self.press = {"source": PALETTE, "index": palette_index, "start": position}
                return
            row = self.row_at(position)
            if row is not None:
                self.press = {"source": PROGRAM, "index": row, "start": position}
                return
        if self.board.map_view.tile_at(position) is None:
            return
        if self.armed_goto is not None:
            self.set_goto_target(self.board.map_view.tile_at(position))
            return
        ghost = self.board.ghost_at(position)
        if ghost is not None:
            self.select_ghost(ghost)

    def mouse_up(self, position):
        press = self.press
        dragging = self.dragging
        self.press = None
        self.dragging = False
        if press is None:
            return
        if dragging:
            self.drop(press, position)
        else:
            self.click(press)

    def click(self, press: dict):
        if press["source"] == PALETTE:
            self.insert(blocks.new_block(blocks.PALETTE[press["index"]]), len(self.current_program))
            return
        program = self.current_program
        block = program[press["index"]]
        if block["type"] == blocks.GOTO:
            self.armed_goto = None if self.armed_goto is block else block
        else:
            program[press["index"]] = blocks.cycle_value(block)

    def drop(self, press: dict, position):
        program = self.current_program
        inside = self.program_rect.collidepoint(position)
        if press["source"] == PALETTE:
            if inside:
                self.insert(blocks.new_block(blocks.PALETTE[press["index"]]), self.insertion_index(position, len(program)))
            return
        block = program.pop(press["index"])
        if inside:
            program.insert(self.insertion_index(position, len(program)), block)
        elif block is self.armed_goto:
            self.armed_goto = None

    def delete_row(self, position):
        if self.selected_ghost is None or self.press is not None:
            return
        row = self.row_at(position)
        if row is not None and self.current_program.pop(row) is self.armed_goto:
            self.armed_goto = None

    def lock(self):
        first_attempt = not self.session.trees
        self.session.trees = [blocks.parse(program) for program in self.programs]
        self.session.seconds_left = max(0.0, self.time_left) if first_attempt else 0.0
        self.game.change_scene(play_scene.PlayScene(self.game, self.session))

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == self.cancel_key:
            self.armed_goto = None
            self.press = None
            self.dragging = False
            return
        if self.forward_event(event):
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.mouse_down(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.delete_row(event.pos)
        elif event.type == pygame.MOUSEMOTION and self.press and not self.dragging:
            start = self.press["start"]
            if math.dist(start, event.pos) > settings.DRAG_THRESHOLD:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.mouse_up(event.pos)
        elif event.type == pygame.MOUSEWHEEL and self.selected_ghost is not None:
            if self.program_rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll = max(0, min(self.max_scroll(), self.scroll - event.y * settings.SCROLL_STEP))

    def update(self, dt: float):
        self.time_left -= dt
        if self.time_left <= 0:
            self.lock()
            return
        self.refresh_labels()
        self.board.update(dt)
        self.update_ui(dt)

    def dragged_block(self) -> dict | None:
        if not self.dragging or self.press is None:
            return None
        if self.press["source"] == PALETTE:
            return blocks.PALETTE[self.press["index"]]
        return self.current_program[self.press["index"]]

    def draw_palette(self, surface: pygame.Surface):
        for template, rect in zip(blocks.PALETTE, self.palette_rects):
            draw_block(surface, template, rect.topleft)

    def draw_program(self, surface: pygame.Surface):
        program = self.current_program
        hidden = self.press["index"] if self.dragging and self.press["source"] == PROGRAM else None
        shown = [block for index, block in enumerate(program) if index != hidden]
        mouse = pygame.mouse.get_pos()
        gap = self.insertion_index(mouse, len(shown)) if self.dragging and self.program_rect.collidepoint(mouse) else None
        indents = blocks.depths(shown)
        surface.set_clip(self.program_rect.inflate(-4, -4))
        for index, block in enumerate(shown):
            slot = index + 1 if gap is not None and index >= gap else index
            top = self.row_top(slot) + (settings.ROW_HEIGHT - self.block_height) // 2
            left = self.program_rect.x + settings.PANEL_PADDING + indents[index] * settings.INDENT
            draw_block(surface, block, (left, top), block is self.armed_goto)
        surface.set_clip(None)

    def draw(self, surface: pygame.Surface):
        surface.fill(settings.BG_COLOR)
        route = self.session.route_tiles if self.session.config["preview"] else ()
        targets = []
        if self.selected_ghost is not None:
            targets = [
                block["target"]
                for block in self.current_program
                if block["type"] == blocks.GOTO and block.get("target")
            ]
        self.board.draw(surface, self.session.start_pellets(), route, targets)
        self.draw_ui(surface)
        if self.selected_ghost is not None:
            self.draw_palette(surface)
            self.draw_program(surface)
        dragged = self.dragged_block()
        if dragged is not None:
            x, y = pygame.mouse.get_pos()
            draw_block(surface, dragged, (x - self.block_width // 2, y - self.block_height // 2))
