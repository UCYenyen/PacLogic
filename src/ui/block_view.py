import pygame

from src.core import settings
from src.core.resource_loader import load_font, load_scaled_image
from src.logic.blocks import label


def block_image(kind: str) -> pygame.Surface:
    return load_scaled_image(settings.UI_BLOCKS[kind], settings.UI_SCALE, settings.BLOCK_PLACEHOLDER_SIZE)


def selected_outline() -> pygame.Surface:
    return load_scaled_image(settings.UI_BLOCK_SELECTED, settings.UI_SCALE, settings.BLOCK_PLACEHOLDER_SIZE)


def block_size() -> tuple[int, int]:
    return block_image("MOVE").get_size()


def draw_block(surface: pygame.Surface, block: dict, topleft, selected: bool = False) -> pygame.Rect:
    image = block_image(block["type"])
    rect = image.get_rect(topleft=topleft)
    surface.blit(image, rect)
    if selected:
        surface.blit(selected_outline(), rect)
    text = load_font(settings.FONT_SMALL).render(label(block), True, settings.TEXT_COLOR)
    surface.blit(text, text.get_rect(midleft=(rect.x + 8, rect.centery)))
    return rect
