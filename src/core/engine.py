import pygame

from src.core import settings
from src.core.session import Session
from src.scenes.base_scene import BaseScene
from src.scenes.menu_scene import MenuScene


class Game:
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
        self.session = Session()
        self.scene: BaseScene = MenuScene(self, self.session)

    def change_scene(self, scene: BaseScene) -> None:
        self.scene.on_exit()
        self.scene = scene
        self.scene.on_enter()

    def quit(self) -> None:
        self.running = False

    def run(self) -> None:
        self.scene.on_enter()
        while self.running:
            dt = min(self.clock.tick(settings.FPS) / 1000.0, settings.MAX_DT)
            self._handle_events()
            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()

        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            else:
                self.scene.handle_event(event)
