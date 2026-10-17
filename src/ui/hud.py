"""HUD overlay and a reusable Button component."""
import pygame

from src.core import settings
from src.core.resource_loader import load_font, load_image


class HUD:
    def __init__(self) -> None:
        self.font = load_font(24)
        self.big_font = load_font(48)

    def draw(self, surface: pygame.Surface, lives: int, score: int, paused: bool = False) -> None:
        lives_text = self.font.render(f"Lives: {lives}", True, settings.WHITE)
        score_text = self.font.render(f"Score: {score}", True, settings.WHITE)
        surface.blit(lives_text, (16, 12))
        surface.blit(score_text, score_text.get_rect(topright=(settings.SCREEN_WIDTH - 16, 12)))

        if paused:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))
            text = self.big_font.render("Paused", True, settings.ACCENT)
            surface.blit(text, text.get_rect(center=surface.get_rect().center))


class Button:
    """Image-backed button with a hover highlight."""

    def __init__(self, label: str, center: tuple[int, int], font: pygame.font.Font) -> None:
        self.image = load_image("ui/button.png")
        self.rect = self.image.get_rect(center=center)
        self.label = font.render(label, True, settings.WHITE)
        self.hovered = False

    def update(self, mouse_pos: tuple[int, int]) -> None:
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.image, self.rect)
        if self.hovered:
            pygame.draw.rect(surface, settings.ACCENT, self.rect, width=3, border_radius=10)
        surface.blit(self.label, self.label.get_rect(center=self.rect.center))
