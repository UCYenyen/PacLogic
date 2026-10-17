from abc import ABC, abstractmethod

import pygame


class Component(ABC):
    visible = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

    def update(self, dt: float):
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface): ...
