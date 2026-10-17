"""Abstract base class every scene (screen / game state) inherits from."""
from abc import ABC, abstractmethod

import pygame


class BaseScene(ABC):
    def __init__(self, game) -> None:
        self.game = game

    def on_enter(self) -> None:
        """Called when the scene becomes active."""

    def on_exit(self) -> None:
        """Called right before the scene is replaced."""

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None: ...

    @abstractmethod
    def update(self, dt: float) -> None: ...

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None: ...
