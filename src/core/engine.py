"""Main Game class: window setup, game loop, and scene management."""
import pygame

from src.core import settings


class Game:
    """Owns the window and clock, and delegates each frame to the active scene."""

    def __init__(self) -> None:
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error as exc:
            print(f"[engine] Audio disabled: {exc}")

        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption(settings.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Imported here to avoid circular imports (scenes receive the Game).
        from src.scenes.menu_scene import MenuScene

        self.scene = MenuScene(self)

    def change_scene(self, scene) -> None:
        """Swap the active scene, calling its lifecycle hooks."""
        self.scene.on_exit()
        self.scene = scene
        self.scene.on_enter()

    def quit(self) -> None:
        self.running = False

    def run(self) -> None:
        self.scene.on_enter()
        while self.running:
            # Seconds since last frame, clamped so a hitch can't tunnel objects.
            dt = min(self.clock.tick(settings.FPS) / 1000.0, 0.05)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                else:
                    self.scene.handle_event(event)

            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
