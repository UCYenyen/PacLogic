"""Main gameplay scene: dodge enemies by jumping, survive as long as possible."""
import random

import pygame

from src.core import settings
from src.entities.enemy import Enemy
from src.entities.player import Player
from src.scenes.base_scene import BaseScene
from src.ui.hud import HUD


class PlayScene(BaseScene):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.player = Player(settings.SCREEN_WIDTH / 2, settings.GROUND_Y)
        self.enemies: pygame.sprite.Group = pygame.sprite.Group()
        self.hud = HUD()
        self.spawn_timer = 0.0
        self.elapsed = 0.0
        self.score = 0
        self.paused = False

    def _spawn_enemy(self) -> None:
        from_left = random.random() < 0.5
        x = -30 if from_left else settings.SCREEN_WIDTH + 30
        speed = settings.ENEMY_SPEED + min(self.elapsed * 4, 200)  # ramps up over time
        self.enemies.add(Enemy(x, direction=1 if from_left else -1, speed=speed))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == settings.KEY_PAUSE:
            self.paused = not self.paused

    def update(self, dt: float) -> None:
        if self.paused:
            return

        self.elapsed += dt
        self.player.handle_input(pygame.key.get_pressed())
        self.player.update(dt)

        self.spawn_timer += dt
        if self.spawn_timer >= settings.ENEMY_SPAWN_INTERVAL:
            self.spawn_timer = 0.0
            self._spawn_enemy()

        before = len(self.enemies)
        self.enemies.update(dt)
        self.score += before - len(self.enemies)  # +1 per enemy that left the screen

        if pygame.sprite.spritecollide(self.player, self.enemies, dokill=False):
            self.player.take_hit()

        if self.player.is_dead:
            from src.scenes.menu_scene import MenuScene

            self.game.change_scene(MenuScene(self.game, message=f"Game Over - Score: {self.score}"))

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(settings.BG_COLOR)
        pygame.draw.rect(
            surface,
            settings.GROUND_COLOR,
            (0, settings.GROUND_Y, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT - settings.GROUND_Y),
        )
        self.enemies.draw(surface)
        if self.player.visible:
            surface.blit(self.player.image, self.player.rect)
        self.hud.draw(surface, lives=self.player.lives, score=self.score, paused=self.paused)
