# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

A 2D Pygame game (Python 3.11+, `pygame-ce`). Entry point is `main.py`, which builds `src.core.engine.Game` and calls `run()`.

## Commands

- Install: `pip install -r requirements.txt`
- Run: `python main.py` (always run from the repo root so `src` imports resolve)
- There is no test suite; do not add tests unless asked.

## Architecture

- **Game loop** (`src/core/engine.py`): `Game` owns the window, clock, and the active scene. Each frame: compute `dt` in seconds (clamped to 0.05), forward events to `scene.handle_event`, then `scene.update(dt)`, then `scene.draw(screen)`.
- **Scenes** (`src/scenes/`): every screen subclasses `BaseScene` and implements `handle_event`, `update(dt)`, `draw(surface)`. Optional hooks are `on_enter` / `on_exit`. Switch scenes with `game.change_scene(NewScene(game))`. Scenes import each other inside methods to avoid circular imports. Keep it that way.
- **Entities** (`src/entities/`): `pygame.sprite.Sprite` subclasses. Track position in floats (`pygame.Vector2` / `pos_x`) and sync to `rect` at the end of `update`. Movement must be `speed * dt` (frame-rate independent).
- **UI** (`src/ui/hud.py`): `HUD` overlay and reusable `Button`.
- **Settings** (`src/core/settings.py`): the single home for constants: screen size, FPS, colors, physics, gameplay tuning, key bindings, and asset paths. Do not hard-code these in other modules.

## Conventions

- Load assets only through `src/core/resource_loader.py` (`load_image`, `load_sound`, `load_font`, `play_music`). Paths are relative to the asset subfolder, e.g. `load_image("sprites/player.png")`, `load_sound("sfx/jump.wav")`. The loaders are cached and return placeholders on failure. Never call `pygame.image.load` directly.
- Every package directory needs an `__init__.py` (double underscores).
- Use type hints and keep modules small and single-purpose.

## Assets

The files in `assets/` are generated placeholders (simple shapes, a synth chirp, an arpeggio loop, and pygame's FreeSans font as `default.ttf`). Replace them freely, keeping the same filenames or updating the paths where they are loaded.
