from abc import ABC, abstractmethod

import pygame


class BaseScene(ABC):
    def __init__(self, game, session):
        self.game = game
        self.session = session
        self.ui = []

    def forward_event(self, event: pygame.event.Event) -> bool:
        handled = False
        for component in reversed(self.ui):
            if component.handle_event(event):
                handled = True
                break
        return handled

    def update_ui(self, dt: float):
        for component in self.ui:
            component.update(dt)

    def draw_ui(self, surface: pygame.Surface):
        for component in self.ui:
            component.draw(surface)

    @abstractmethod
    def handle_event(self, event: pygame.event.Event): ...

    @abstractmethod
    def update(self, dt: float): ...

    @abstractmethod
    def draw(self, surface: pygame.Surface): ...
