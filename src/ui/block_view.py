import pygame

from src.core import settings
from src.core.resource_loader import load_font, load_scaled_image
from src.logic.blocks import COUNT_RANGES, MOVE, REPEAT


def block_image(block: dict) -> pygame.Surface:
    path = settings.UI_MOVE_BLOCKS[block["dir"]] if block["type"] == MOVE else settings.UI_BLOCKS[block["type"]]
    return load_scaled_image(path, settings.UI_SCALE, settings.BLOCK_PLACEHOLDER_SIZE)


def block_size() -> tuple[int, int]:
    return block_image({"type": REPEAT}).get_size()


def draw_block(surface: pygame.Surface, block: dict, topleft) -> pygame.Rect:
    image = block_image(block)
    rect = image.get_rect(topleft=topleft)
    surface.blit(image, rect)
    if block["type"] in COUNT_RANGES:
        box = pygame.Rect([value * settings.UI_SCALE for value in settings.COUNT_BOX]).move(rect.topleft)
        text = load_font(settings.FONT_SMALL).render(f"{block['n']}x", True, settings.COUNT_COLOR)
        surface.blit(text, text.get_rect(center=box.center))
    return rect
