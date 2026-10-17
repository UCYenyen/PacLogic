# My Pygame Game

A starter Pygame project with a scene system, safe asset loading, a player, enemies, and a HUD.

The demo gameplay is simple: jump over the enemies walking along the ground. You get a point for each enemy that leaves the screen, and enemies get faster over time.

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

| Action       | Keys                    |
|--------------|-------------------------|
| Move         | ← → / A D               |
| Jump         | Space / ↑ / W           |
| Start (menu) | Enter / Space / click   |
| Pause / Quit | Esc                     |

## Project structure

```text
main.py                 Entry point
assets/                 Fonts, images, sounds (placeholders, replace freely)
src/core/engine.py      Game class: window, main loop, scene switching
src/core/settings.py    Constants: screen size, FPS, colors, physics, keys, paths
src/core/resource_loader.py  Cached asset loaders with fallbacks
src/entities/           Player, Enemy sprites
src/scenes/             BaseScene, MenuScene, PlayScene
src/ui/hud.py           HUD overlay and Button
```

## Adding a new scene

1. Create `src/scenes/my_scene.py` with a class that subclasses `BaseScene` and implements `handle_event`, `update(dt)`, and `draw(surface)`.
2. Switch to it with `self.game.change_scene(MyScene(self.game))`.
