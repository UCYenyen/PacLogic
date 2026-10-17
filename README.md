# PacLogic

A Pygame project skeleton with a game loop, a scene system, and safe asset loading. Gameplay is not implemented yet.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> `pygame-ce` and `pygame` share the `pygame` import name. Install only one of them in an environment.

## Run

```bash
python main.py
```

## Project structure

```text
main.py                      Entry point
assets/                      Fonts, images, sounds (placeholders, replace freely)
src/core/engine.py           Game class: window, main loop, scene switching
src/core/settings.py         Constants: screen size, FPS, colors, paths
src/core/resource_loader.py  Cached asset loaders with fallbacks
src/entities/                Player, Enemy (empty stubs)
src/scenes/                  BaseScene, MenuScene, PlayScene (empty stubs)
src/ui/hud.py                HUD (empty stub)
```

## Adding a new scene

1. Create `src/scenes/my_scene.py` with a class that subclasses `BaseScene` and implements `handle_event`, `update(dt)`, and `draw(surface)`.
2. Switch to it with `self.game.change_scene(MyScene(self.game))`.
