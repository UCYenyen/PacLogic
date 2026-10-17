"""Player-controlled character with horizontal movement, gravity, and jumping."""
import pygame

from src.core import settings
from src.core.resource_loader import load_image, load_sound


class Player(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, image: pygame.Surface | None = None) -> None:
        super().__init__()
        self.image = image if image is not None else load_image("sprites/player.png")
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.pos = pygame.Vector2(self.rect.midbottom)
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = True
        self.lives = settings.PLAYER_LIVES
        self.invulnerable_timer = 0.0
        self.direction = 0  # -1 left, 0 idle, 1 right

    # --- Input ---
    def handle_input(self, keys) -> None:
        left = any(keys[k] for k in settings.KEYS_LEFT)
        right = any(keys[k] for k in settings.KEYS_RIGHT)
        self.direction = int(right) - int(left)
        if any(keys[k] for k in settings.KEYS_JUMP):
            self.jump()

    def jump(self) -> bool:
        """Jump if standing on the ground. Returns True if the jump happened."""
        if not self.on_ground:
            return False
        self.velocity.y = -settings.PLAYER_JUMP_SPEED
        self.on_ground = False
        load_sound("sfx/jump.wav", volume=0.4).play()
        return True

    # --- Simulation ---
    def update(self, dt: float) -> None:
        self.velocity.x = self.direction * settings.PLAYER_SPEED
        self.velocity.y += settings.GRAVITY * dt
        self.pos += self.velocity * dt

        # Ground collision
        if self.pos.y >= settings.GROUND_Y:
            self.pos.y = settings.GROUND_Y
            self.velocity.y = 0
            self.on_ground = True

        # Keep inside the screen horizontally
        half_w = self.rect.width / 2
        self.pos.x = max(half_w, min(settings.SCREEN_WIDTH - half_w, self.pos.x))

        if self.invulnerable_timer > 0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)

        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))

    def take_hit(self) -> bool:
        """Lose a life unless invulnerable. Returns True if damage was applied."""
        if self.invulnerable_timer > 0 or self.lives <= 0:
            return False
        self.lives -= 1
        self.invulnerable_timer = settings.INVULNERABLE_TIME
        return True

    @property
    def is_dead(self) -> bool:
        return self.lives <= 0

    @property
    def visible(self) -> bool:
        """Blink while invulnerable."""
        return self.invulnerable_timer <= 0 or int(self.invulnerable_timer * 10) % 2 == 0
