import pygame

from src.core import settings
from src.core.resource_loader import load_scaled_image
from src.ui.component import Component


def _scaled_piece(source: pygame.Surface, area: tuple, size: tuple) -> pygame.Surface | None:
    if area[2] <= 0 or area[3] <= 0 or size[0] <= 0 or size[1] <= 0:
        return None
    return pygame.transform.scale(source.subsurface(area), size)


def nine_slice(source: pygame.Surface, border: int, size: tuple) -> pygame.Surface:
    width, height = size
    source_width, source_height = source.get_size()
    edge = max(0, min(border, source_width // 2, source_height // 2, width // 2, height // 2))
    inner_source_w = source_width - 2 * edge
    inner_source_h = source_height - 2 * edge
    inner_w = width - 2 * edge
    inner_h = height - 2 * edge
    result = pygame.Surface((width, height), pygame.SRCALPHA)
    pieces = (
        ((0, 0, edge, edge), (edge, edge), (0, 0)),
        ((source_width - edge, 0, edge, edge), (edge, edge), (width - edge, 0)),
        ((0, source_height - edge, edge, edge), (edge, edge), (0, height - edge)),
        ((source_width - edge, source_height - edge, edge, edge), (edge, edge), (width - edge, height - edge)),
        ((edge, 0, inner_source_w, edge), (inner_w, edge), (edge, 0)),
        ((edge, source_height - edge, inner_source_w, edge), (inner_w, edge), (edge, height - edge)),
        ((0, edge, edge, inner_source_h), (edge, inner_h), (0, edge)),
        ((source_width - edge, edge, edge, inner_source_h), (edge, inner_h), (width - edge, edge)),
        ((edge, edge, inner_source_w, inner_source_h), (inner_w, inner_h), (edge, edge)),
    )
    for area, piece_size, destination in pieces:
        piece = _scaled_piece(source, area, piece_size)
        if piece is not None:
            result.blit(piece, destination)
    return result


class Panel(Component):
    def __init__(self, rect, image_path: str = settings.UI_PANEL, border: int = settings.UI_PANEL_BORDER):
        source = load_scaled_image(image_path, settings.UI_SCALE, settings.PANEL_PLACEHOLDER_SIZE)
        self.rect = pygame.Rect(rect)
        self.surface = nine_slice(source, border * settings.UI_SCALE, self.rect.size)

    def draw(self, surface: pygame.Surface):
        if self.visible:
            surface.blit(self.surface, self.rect)
