# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

```bash
python main.py
```

No dependencies — stdlib only. Python 3.x required. No build step, no virtual environment needed.

There is no automated test suite. Testing is done by running the game and playing through scenarios manually.

## Architecture Overview

RiftTracker is a text-based, turn-based dungeon-crawling RPG. The entry point is `main.py`, which owns the title screen, character creation, save/load selection, and the main camp loop. Everything else lives in the `game/` package.

**Data flow at a glance:**

```
main.py
  └─ Camp menu
       ├─ Explore  →  world.py  →  combat.py  →  enemies.py / items.py
       ├─ Character sheet / Inventory / Skills  →  menus.py  →  character.py
       ├─ World map  →  worldmap.py
       └─ Save / Load  →  saveload.py
```

**Key modules:**

| File | Responsibility |
|------|---------------|
| `game/character.py` | `Character` class — stats, leveling, inventory, equipment, skills |
| `game/stats.py` | Class base stats (`CLASS_BASES`), derived stat formulas (damage, dodge, crit) |
| `game/combat.py` | Turn-based combat engine: `run_combat()`, HUD, skill/attack resolution, status effects |
| `game/enemies.py` | `Enemy` class, 30+ enemy templates, 4 boss templates, enemy scaling logic |
| `game/items.py` | `Weapon`, `Armor`, `Consumable`, `SkillBook` classes; all item definitions and loot tables |
| `game/skills.py` | Skill definitions (20+ skills), execution logic, cooldowns, effects |
| `game/world.py` | 11 explorable zones, random event weights (combat/loot/merchant/shrine/books) |
| `game/worldmap.py` | World map display, zone unlock tracking, boss kill status |
| `game/menus.py` | In-camp UI: character sheet, stat allocation, inventory management, skill viewer |
| `game/ui.py` | Terminal utilities: ANSI colors, slow-print, menus, progress bars, fast-mode toggle |
| `game/saveload.py` | JSON serialization/deserialization of `Character` and item registry into `saves/` |

## Key Design Patterns

**Character state is the single source of truth.** `Character` holds all player stats, inventory, equipped items, known skills, and progression. `menus.py` and `combat.py` operate on the character object passed in — they do not own state.

**Stats flow:** Core stats (STR/INT/AGI/VIT/LCK/PER) → derived stats computed via formulas in `stats.py` → used in combat resolution in `combat.py`. Equipment bonuses are added on top.

**Item identity:** Items have an `item_id` string key. `saveload.py` serializes only the id (plus quantity/charges), then reconstructs full item objects from the registry on load. When adding new items, register them in `items.py` with a unique id.

**Enemy scaling:** Enemy stats scale based on zone level. Bosses are defined separately and do not scale — they have fixed stat blocks in `enemies.py`.

**Save format:** JSON files in `saves/<character_name>.json`. The structure mirrors the `Character` object fields plus an item registry snapshot.
