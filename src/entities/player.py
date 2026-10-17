from src.core import settings
from src.entities.character import Character


class Player(Character):
    def __init__(self, scale: int):
        super().__init__(
            settings.PACMAN_SPRITE_DIR,
            settings.PACMAN_ACTION,
            scale,
            settings.PACMAN_FRAME_DURATION,
            settings.PAC_START_DIRECTION,
        )
