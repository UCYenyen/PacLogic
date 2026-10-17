# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

PacLogic: a 2D Pygame game (Python 3.11+, `pygame-ce`). Entry point is `main.py`, which builds `src.core.engine.Game` and calls `run()`.

### Game concept

PacLogic is reverse Pac-Man. Pac-Man is an AI that uses A* to find the shortest route to an exit tile (and, in pellet mode, eats every pellet first). The player controls 1 to 4 ghosts, but only by writing small drag-and-drop block programs before the round starts. Once the round runs, the programs act alone, and the ghosts win by catching Pac-Man before he escapes.

- The game runs in discrete ticks, not free movement. Every tick, each ghost acts first, then Pac-Man takes one step.
- Ghosts can never enter the safe zone: every tile within maze distance `SAFE_RADIUS` of the exit.
- Outcomes: caught (ghosts win), escaped (Pac-Man wins), or blocked (the tick cap ran out).

### Logic layer

All game rules live in `src/logic/` as pure Python with no pygame imports:

- `grid.py`: levels, parsing, validation, BFS distances, safe zone, maze generator.
- `search.py`: Pac-Man's search (A*, UCS, greedy, BFS) and heuristics.
- `sim.py`: the tick simulation, Pac-Man's brain, scoring, and scripted ghost controllers.
- `blocks.py`: the block language (parse and run ghost programs).

Scenes, entities, and UI only read from this logic and never change the rules. All tuning values live in `src/core/settings.py`, which must stay free of pygame imports so the logic layer can use it.

## Commands

- Install: `pip install -r requirements.txt`
- Run: `python main.py` (always run from the repo root so `src` imports resolve)
- There is no test suite; do not add tests unless asked.

## Architecture

- **Game loop** (`src/core/engine.py`): `Game` owns the window, clock, the shared `Session`, and the active scene. Each frame: compute `dt` in seconds (clamped to `MAX_DT`), forward events to `scene.handle_event`, then `scene.update(dt)`, then `scene.draw(screen)`. The game starts in `MenuScene`.
- **Session** (`src/core/session.py`): the menu options, the chosen level, the per-ghost block programs (flat lists) and parsed trees, and the planning time left. It is passed from scene to scene.
- **Scenes** (`src/scenes/`): `MenuScene` → `PreviewScene` → `PlanScene` → `PlayScene` → `ResultScene`. Every scene subclasses `BaseScene`, takes `(game, session)`, and implements `handle_event`, `update(dt)`, `draw(surface)`. Each scene keeps its UI components in `self.ui`, uses `forward_event`, `update_ui`, and `draw_ui` from `BaseScene`, and switches with `game.change_scene(NewScene(game, session))`. When two scenes reference each other, import the module at the top of the file (`from src.scenes import play_scene`) and access the class at call time (`play_scene.PlayScene(self.game, self.session)`) so the circular import resolves.
- **Plan scene**: the player clicks a ghost on the map to select it. The ghost switches to its `selected/` sprite and the block palette and program panel (`src/ui/program_editor.py`) appear for that ghost.
- **Entities** (`src/entities/`): `Player` (Pac-Man) and `Enemy` (ghost) subclass `Character` and are display-only sprites driven by the `Sim`; they hold no rules. `Animator` plays one animation per direction. Movement is tick-based: sprites are drawn at `lerp(previous_tile, tile, tick_progress)`. This is an intentional exception to the `speed * dt` rule; animation frames still advance with `dt`.
- **UI** (`src/ui/`): everything a scene puts in `self.ui` subclasses `Component` (no-op `handle_event` and `update`, a `visible` flag, and an abstract `draw`). `MapView` (tile-image map), `Board` (map plus character sprites), `ImageButton`, `Panel` (9-slice), `Label`, `FlashMessage`, `Image`, `HUD`, `ProgramEditor`, and `block_view`.
- **Settings** (`src/core/settings.py`): the single home for constants: screen size, tuning values, the difficulty and score tables, layout rects and absolute screen positions, key names, and every image path. Offsets measured from a panel's own rect may stay in the scene. Do not hard-code these in other modules.

## Drawing rules

- Everything on screen uses images exported from Aseprite. Never draw characters, tiles, buttons, panels, or blocks with `pygame.draw`; the only exceptions are debug overlays and text.
- Never bake changing text (timer, score, numbers, block labels) into images; draw the empty art and render text on top with `Label` or `load_font`.
- Scale pixel art with `pygame.transform.scale` by an integer factor, once at load time. Never use `smoothscale`. Map art uses the largest integer scale up to `ART_SCALE` that fits the scene's map rect; UI art uses `UI_SCALE`.
- Missing images fall back to the loader's magenta placeholder, so a planned image path can be used before the art exists.

## Code Rules

- Never write comments. This includes `#` comments and docstrings (module, class, and function). Use clear names instead.
- All imports go at the top of the file, before any other code. Never import inside a function, method, class body, or conditional block.

## Git

- Every feature gets its own branch, named after the feature (e.g. `player-movement`). Create the branch before starting the feature and commit the work to it.
- Never add Claude as an author, contributor, or co-author anywhere on GitHub. No `Co-Authored-By: Claude` trailers, no "Generated with Claude Code" lines, and no Claude attribution in commit messages, PR titles, or PR descriptions.

## Conventions

- Load assets only through `src/core/resource_loader.py` (`load_image`, `load_sound`, `load_font`, `play_music`). Paths are relative to the asset subfolder, e.g. `load_image("sprites/pacman/eat-up/eat-up-1.png")`, `load_sound("sfx/jump.wav")`. The loaders are cached and return placeholders on failure. Never call `pygame.image.load` directly.
- Do not create `__init__.py` files. Packages are namespace packages, and imports always use the full module path (`from src.entities.enemy import Enemy`).
- Use type hints for parameters and for functions that return a value, but never write `-> None`.
- Prefix only module-level helpers with `_`; methods never use a leading underscore.
- Keep modules small and single-purpose.

## Assets

### Character sprites and animation

Every character is animated per direction. Each character must have one animation folder for each of the four directions: up, down, left, right. Never use a single static image for a character, and never flip or rotate one direction's frames to fake another.

Layout under `assets/images/sprites/`:

```text
pacman/
  eat-up/      eat-up-1.png    eat-up-2.png    eat-up-3.png
  eat-down/    eat-down-1.png  ...
  eat-left/    eat-left-1.png  ...
  eat-right/   eat-right-1.png ...
  pacman.aseprite
ghosts/
  red-ghost/
    move-up/      move-up-1.png    move-up-2.png
    move-down/    move-down-1.png  ...
    move-left/    move-left-1.png  ...
    move-right/   move-right-1.png ...
    selected/     selected-down-.png
    red-ghost.aseprite
```

Naming rules:

- Folder: `<action>-<direction>/`. File: `<action>-<direction>-<frame>.png`. Frames are numbered from 1 with no gaps, and play in that order.
- Pac-Man's action is `eat` (3 frames per direction). Ghosts use `move` (2 frames per direction). Each ghost has its own folder under `ghosts/` (e.g. `red-ghost/`), and new ghosts must follow the same structure.
- Frame counts differ per character, so animation code must find the frames in a folder instead of hard-coding the count. Sort frames by their number as an integer, not as text, so `10` comes after `9`.
- An entity picks its animation from its current direction (`up`, `down`, `left`, `right`), advances frames using `dt`, and loops. Keep the last direction when the character stops.
- `.aseprite` files are the editable sources for the art. The game never loads them, only the exported `.png` frames.
- `ghosts/red-ghost/selected/` holds an extra state sprite, separate from the movement animations.

### Other sprites

- `items/coin/coin.png`: collectible coin.
- `tile/wall-tile.png`, `tile/empty-tile.png`: map tiles. `tile/path/path-preview.png`: path preview overlay.

### Placeholders

`fonts/default.ttf` (pygame's FreeSans), `images/ui/button.png`, `sounds/music/bgm.ogg`, and `sounds/sfx/jump.wav` are generated placeholders. Replace them freely, keeping the same filenames or updating the paths where they are loaded.
