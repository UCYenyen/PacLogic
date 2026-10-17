# PacLogic

Reverse Pac-Man. Pac-Man is an AI that uses A* to find the shortest route to the exit. You control 1 to 4 ghosts, but only by writing small drag-and-drop block programs before the round starts. Once the round runs, the programs act alone, and the ghosts win by catching Pac-Man before he escapes.

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

## How to play

1. **Menu**: press PLAY to open Game setup. Use the left and right arrows beside each option to pick the level, Pac-Man AI, ghost count, win mode, and planning time, then press Continue.
2. **Preview**: check the map and level info, then press Start planning.
3. **Plan**: click a ghost on the map to program it.
   - Click a palette block to append it, or drag it between rows to insert it.
   - Drag a program block to reorder it. Drag it out of the panel or right click it to delete it.
   - Click REPEAT or IF PAC WITHIN to cycle its number.
   - Click a GOTO block, then click a map tile to set its target (Esc cancels).
   - Press Lock & Run, or wait for the timer to reach 0.
4. **Run**: SPACE pauses, F toggles speed between x1 and x4.
5. **Result**: Replay, edit the programs, or go back to the menu.

## Project structure

```text
main.py                      Entry point
assets/levels/               Handmade levels (ASCII: # wall, . floor, P Pac-Man, E exit, G ghost, o pellet)
assets/images/               Sprites, tiles, and UI art (missing art shows a magenta placeholder)
src/core/                    Engine, settings, session, resource loader
src/logic/                   Pure-Python rules: grid, search, sim, blocks
src/entities/                Pac-Man and ghost sprites, Animator
src/scenes/                  Menu, Preview, Plan, Play, Result
src/ui/                      Map view, board, buttons, panels, labels, HUD
```
