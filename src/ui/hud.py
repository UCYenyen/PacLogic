import pygame

from src.core import settings
from src.ui.label import Label
from src.ui.panel import Panel

STAT_ROWS = 9


class HUD:
    def __init__(self, rect=settings.HUD_PANEL_RECT):
        self.panel = Panel(rect)
        left = self.panel.rect.x + 20
        top = self.panel.rect.y + 20
        self.title = Label("Run", (left, top), settings.FONT_LARGE, settings.ACCENT_COLOR)
        self.rows = [Label("", (left, top + 80 + row * 34)) for row in range(STAT_ROWS)]
        self.hint = Label(
            "SPACE pause   F speed",
            (left, self.panel.rect.bottom - 40),
            settings.FONT_SMALL,
            settings.TEXT_DIM_COLOR,
        )

    def update_stats(self, sim, speed: int, paused: bool):
        brain = sim.brain
        texts = [
            f"Tick {sim.tick} / {sim.tick_cap}",
            f"A* plans made: {brain.plans_made}",
            f"Nodes expanded: {brain.nodes_expanded}",
            f"Last plan: {brain.last_ms:.2f} ms",
            f"Slowest plan: {brain.slowest_ms:.2f} ms",
            f"Pellets left: {len(sim.pellets)}",
            f"AI: {sim.difficulty}",
            f"Speed: x{speed}",
            "PAUSED" if paused else "",
        ]
        for label, text in zip(self.rows, texts):
            label.set_text(text, settings.WARNING_COLOR if text == "PAUSED" else settings.TEXT_COLOR)

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface):
        self.panel.draw(surface)
        self.title.draw(surface)
        for label in self.rows:
            label.draw(surface)
        self.hint.draw(surface)
