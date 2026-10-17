from src.core import settings
from src.core.resource_loader import has_frames, list_folders, load_animation
from src.entities.character import Character


def ghost_art_ready(name: str) -> bool:
    base = f"{settings.GHOST_SPRITE_DIR}/{name}"
    return all(
        has_frames(f"{base}/{settings.GHOST_ACTION}-{direction}")
        for direction in settings.DIRECTION_NAMES.values()
    )


def ghost_art_folders(count: int) -> tuple[list, list]:
    ordered = [name for name in settings.GHOST_ORDER if ghost_art_ready(name)]
    extras = [
        name
        for name in list_folders(settings.GHOST_SPRITE_DIR)
        if name not in settings.GHOST_ORDER and ghost_art_ready(name)
    ]
    available = ordered + extras or [settings.GHOST_ORDER[0]]
    missing = [name for name in settings.GHOST_ORDER[:count] if name not in available]
    folders = [f"{settings.GHOST_SPRITE_DIR}/{available[index % len(available)]}" for index in range(count)]
    return folders, missing


class Enemy(Character):
    def __init__(self, folder: str, scale: int):
        super().__init__(
            folder,
            settings.GHOST_ACTION,
            scale,
            settings.GHOST_FRAME_DURATION,
            settings.GHOST_START_DIRECTION,
        )
        self.selected_image = load_animation(f"{folder}/{settings.GHOST_SELECTED_FOLDER}", scale)[0]
        self.selected = False

    def update(self, dt: float):
        super().update(dt)
        if self.selected:
            self.image = self.selected_image
