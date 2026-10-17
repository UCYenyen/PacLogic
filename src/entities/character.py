from src.entities.animator import load_directional_animator


def lerp_tile(previous_tile, tile, progress: float) -> tuple[float, float]:
    return (
        previous_tile[0] + (tile[0] - previous_tile[0]) * progress,
        previous_tile[1] + (tile[1] - previous_tile[1]) * progress,
    )


class Character:
    def __init__(self, folder: str, action: str, scale: int, frame_duration: float, direction: str):
        self.animator = load_directional_animator(folder, action, scale, frame_duration, direction)
        self.image = self.animator.image
        self.rect = self.image.get_rect()

    def follow(self, previous_tile, tile, direction: str | None, progress: float, map_view):
        self.animator.set_direction(direction)
        self.rect.center = map_view.tile_center(*lerp_tile(previous_tile, tile, progress))

    def update(self, dt: float):
        self.animator.update(dt)
        self.image = self.animator.image
