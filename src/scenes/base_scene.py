from abc import ABC, abstractmethod

import pygame


class BaseScene(ABC):
    def __init__(self, game) -> None:
        self.game = game

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None: ...

    @abstractmethod
    def update(self, dt: float) -> None: ...

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None: ...
