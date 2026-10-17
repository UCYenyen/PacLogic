import pygame

from src.core import settings
from src.core.resource_loader import load_font, load_scaled_image
from src.logic.grid import Level


def fit_scale(level: Level, area: pygame.Rect) -> int:
    for scale in range(settings.ART_SCALE, 0, -1):
        tile = settings.TILE_SIZE * scale
        if level.width * tile <= area.width and level.height * tile <= area.height:
            return scale
    return 1


class MapView:
    def __init__(self, level: Level, area):
        self.level = level
        self.area = pygame.Rect(area)
        self.scale = fit_scale(level, self.area)
        self.tile_px = settings.TILE_SIZE * self.scale
        self.rect = pygame.Rect(0, 0, level.width * self.tile_px, level.height * self.tile_px)
        self.rect.center = self.area.center
        fallback = (settings.TILE_SIZE, settings.TILE_SIZE)
        self.wall = load_scaled_image(settings.TILE_WALL, self.scale, fallback)
        self.floor = load_scaled_image(settings.TILE_FLOOR, self.scale, fallback)
        self.pellet = load_scaled_image(settings.TILE_PELLET, self.scale, fallback)
        self.route = load_scaled_image(settings.TILE_ROUTE, self.scale, fallback)
        self.exit = load_scaled_image(settings.TILE_EXIT, self.scale, fallback)
        self.safe_zone = load_scaled_image(settings.TILE_SAFE_ZONE, self.scale, fallback)
        self.cost_inset = settings.ROUTE_TILE_BORDER * self.scale + settings.COST_TEXT_GAP
        self.cost_fonts = [load_font(size) for size in settings.COST_FONT_SIZES]
        self.background = self.render_background()
        self.safe_zone_layer = self.render_safe_zone_layer()

    def local_topleft(self, tile) -> tuple[int, int]:
        return tile[0] * self.tile_px, tile[1] * self.tile_px

    def render_background(self) -> pygame.Surface:
        surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        for y in range(self.level.height):
            for x in range(self.level.width):
                tile = (x, y)
                surface.blit(self.wall if tile in self.level.walls else self.floor, self.local_topleft(tile))
        return surface

    def render_safe_zone_layer(self) -> pygame.Surface:
        surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        for tile in self.level.safe_zone:
            surface.blit(self.safe_zone, self.local_topleft(tile))
        surface.blit(self.exit, self.local_topleft(self.level.goal))
        return surface

    def tile_topleft(self, tile) -> tuple[int, int]:
        return self.rect.x + tile[0] * self.tile_px, self.rect.y + tile[1] * self.tile_px

    def tile_center(self, x: float, y: float) -> tuple[int, int]:
        return (
            round(self.rect.x + x * self.tile_px + self.tile_px / 2),
            round(self.rect.y + y * self.tile_px + self.tile_px / 2),
        )

    def tile_at(self, position) -> tuple[int, int] | None:
        if not self.rect.collidepoint(position):
            return None
        return (position[0] - self.rect.x) // self.tile_px, (position[1] - self.rect.y) // self.tile_px

    def draw(self, surface: pygame.Surface, pellets=(), route=()):
        surface.blit(self.background, self.rect)
        for tile, _, _ in route:
            surface.blit(self.route, self.tile_topleft(tile))
        surface.blit(self.safe_zone_layer, self.rect)
        for tile in pellets:
            surface.blit(self.pellet, self.tile_topleft(tile))
        self.draw_costs(surface, route)

    def cost_font(self, labels: list):
        room = self.tile_px - 2 * self.cost_inset
        for font in self.cost_fonts:
            widest = max((font.size(label)[0] for label in labels), default=0)
            if widest <= room and 2 * font.size("g")[1] <= room:
                return font
        return self.cost_fonts[-1]

    def draw_costs(self, surface: pygame.Surface, route):
        latest = {tile: (f"g={g}", f"h={h}") for tile, g, h in route}
        font = self.cost_font([label for pair in latest.values() for label in pair])
        for tile, (g_label, h_label) in latest.items():
            left, top = self.tile_topleft(tile)
            inner = pygame.Rect(left, top, self.tile_px, self.tile_px).inflate(-2 * self.cost_inset, -2 * self.cost_inset)
            g_text = font.render(g_label, settings.FONT_ANTIALIAS, settings.COST_G_COLOR)
            h_text = font.render(h_label, settings.FONT_ANTIALIAS, settings.COST_H_COLOR)
            surface.blit(g_text, inner.topleft)
            surface.blit(h_text, h_text.get_rect(bottomleft=inner.bottomleft))
