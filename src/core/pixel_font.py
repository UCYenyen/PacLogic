from functools import lru_cache

import pygame

FIRST_CHARACTER = 32
LAST_ASCII = 126
SKIP_MARKER = (255, 0, 0)


def find_glyphs(sheet: pygame.Surface) -> list:
    width, height = sheet.get_size()
    key = sheet.get_at((0, 0))
    glyphs = []
    x, y, row_height = 0, 0, 1
    while True:
        while sheet.get_at((x, y)) == key:
            x += 1
            if x >= width:
                x, y, row_height = 0, y + row_height, 1
                if y >= height:
                    return glyphs
        glyph_width = 0
        while x + glyph_width < width and sheet.get_at((x + glyph_width, y)) != key:
            glyph_width += 1
        glyph_height = 0
        while y + glyph_height < height and sheet.get_at((x, y + glyph_height)) != key:
            glyph_height += 1
        usable = tuple(sheet.get_at((x, y)))[:3] != SKIP_MARKER
        glyphs.append(pygame.Rect(x, y, glyph_width, glyph_height) if usable else None)
        x += glyph_width
        row_height = glyph_height


class PixelFont:
    def __init__(self, sheet: pygame.Surface, scale: int):
        self.sheet = sheet
        self.scale = scale
        self.glyphs = find_glyphs(sheet)
        ascii_glyphs = [glyph for glyph in self.glyphs[: LAST_ASCII - FIRST_CHARACTER + 1] if glyph is not None]
        self.height = max(glyph.height for glyph in ascii_glyphs)
        self.space_width = self.glyph(" ").width

    def glyph(self, character: str) -> pygame.Rect | None:
        index = ord(character) - FIRST_CHARACTER
        return self.glyphs[index] if 0 <= index < len(self.glyphs) else None

    @lru_cache(maxsize=None)
    def render(self, text: str, antialias: bool = False, color=(255, 255, 255)) -> pygame.Surface:
        width = sum(self.advance(character) for character in text)
        surface = pygame.Surface((max(1, width), self.height), pygame.SRCALPHA)
        x = 0
        for character in text:
            area = self.glyph(character)
            if area is not None:
                mask = pygame.mask.from_surface(self.sheet.subsurface(area))
                surface.blit(mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0)), (x, 0))
            x += self.advance(character)
        if self.scale == 1:
            return surface
        return pygame.transform.scale(surface, (surface.get_width() * self.scale, surface.get_height() * self.scale))

    def advance(self, character: str) -> int:
        area = self.glyph(character)
        return area.width if area is not None else self.space_width
