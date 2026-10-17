# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

PacLogic: a 2D Pygame game (Python 3.11+, `pygame-ce`). Entry point is `main.py`, which builds `src.core.engine.Game` and calls `run()`.

Gameplay is being written from scratch by the user. `Player`, `Enemy`, `MenuScene`, `PlayScene`, and `HUD` are intentionally empty stubs. Do not add gameplay logic unless asked.

## Commands

- Install: `pip install -r requirements.txt`
- Run: `python main.py` (always run from the repo root so `src` imports resolve)
- There is no test suite; do not add tests unless asked.

## Architecture

- **Game loop** (`src/core/engine.py`): `Game` owns the window, clock, and the active scene. Each frame: compute `dt` in seconds (clamped to 0.05), forward events to `scene.handle_event`, then `scene.update(dt)`, then `scene.draw(screen)`. The game starts in `MenuScene`.
- **Scenes** (`src/scenes/`): every screen subclasses `BaseScene` and implements `handle_event`, `update(dt)`, `draw(surface)`. Optional hooks are `on_enter` / `on_exit`. Switch scenes with `game.change_scene(NewScene(game))`. When two scenes reference each other, import the module at the top of the file (`from src.scenes import play_scene`) and access the class at call time (`play_scene.PlayScene(self.game)`) so the circular import resolves.
- **Entities** (`src/entities/`): `pygame.sprite.Sprite` subclasses with `update(dt)`. Movement should be `speed * dt` (frame-rate independent).
- **UI** (`src/ui/`): HUD and other UI components.
- **Settings** (`src/core/settings.py`): the single home for constants (screen size, FPS, colors, asset paths, and any future tuning values or key bindings). Do not hard-code these in other modules.

## Code Rules

- Never write comments. This includes `#` comments and docstrings (module, class, and function). Use clear names instead.
- All imports go at the top of the file, before any other code. Never import inside a function, method, class body, or conditional block.

## Git

- Every feature gets its own branch, named after the feature (e.g. `player-movement`). Create the branch before starting the feature and commit the work to it.
- Never add Claude as an author, contributor, or co-author anywhere on GitHub. No `Co-Authored-By: Claude` trailers, no "Generated with Claude Code" lines, and no Claude attribution in commit messages, PR titles, or PR descriptions.

## Conventions

- Load assets only through `src/core/resource_loader.py` (`load_image`, `load_sound`, `load_font`, `play_music`). Paths are relative to the asset subfolder, e.g. `load_image("sprites/player.png")`, `load_sound("sfx/jump.wav")`. The loaders are cached and return placeholders on failure. Never call `pygame.image.load` directly.
- Every package directory needs an `__init__.py` (double underscores).
- Use type hints and keep modules small and single-purpose.

## Assets

The files in `assets/` are generated placeholders (simple shapes, a synth chirp, an arpeggio loop, and pygame's FreeSans font as `default.ttf`). Replace them freely, keeping the same filenames or updating the paths where they are loaded.
