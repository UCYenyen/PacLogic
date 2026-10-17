"""Title / main menu screen."""
import pygame

from src.core import settings
from src.core.resource_loader import load_font, play_music
from src.scenes.base_scene import BaseScene
from src.ui.hud import Button


class MenuScene(BaseScene):
    def __init__(self, game, message: str | None = None) -> None:
        super().__init__(game)
        self.title_font = load_font(64)
        self.text_font = load_font(24)
        self.message = message  # e.g. "Game Over - Score: 12"
        cx = settings.SCREEN_WIDTH // 2
        self.play_button = Button("Play", center=(cx, 300), font=self.text_font)
        self.quit_button = Button("Quit", center=(cx, 380), font=self.text_font)

    def on_enter(self) -> None:
        play_music("music/bgm.ogg", volume=0.3)

    def _start_game(self) -> None:
        from src.scenes.play_scene import PlayScene

        self.game.change_scene(PlayScene(self.game))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in settings.KEYS_CONFIRM:
                self._start_game()
            elif event.key == settings.KEY_PAUSE:
                self.game.quit()
        if self.play_button.is_clicked(event):
            self._start_game()
        elif self.quit_button.is_clicked(event):
            self.game.quit()

    def update(self, dt: float) -> None:
        mouse = pygame.mouse.get_pos()
        self.play_button.update(mouse)
        self.quit_button.update(mouse)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(settings.BG_COLOR)
        cx = settings.SCREEN_WIDTH // 2

        title = self.title_font.render(settings.TITLE, True, settings.ACCENT)
        surface.blit(title, title.get_rect(center=(cx, 140)))

        if self.message:
            msg = self.text_font.render(self.message, True, settings.WHITE)
            surface.blit(msg, msg.get_rect(center=(cx, 220)))

        self.play_button.draw(surface)
        self.quit_button.draw(surface)

        hint = self.text_font.render("Enter / Space to play  -  Esc to quit", True, (150, 150, 170))
        surface.blit(hint, hint.get_rect(center=(cx, settings.SCREEN_HEIGHT - 40)))
