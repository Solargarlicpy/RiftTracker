"""
Save / Load game — JSON-based, one file per character in saves/.
Items are serialized by name; looked up from static pools on load.
"""
import json
import os
from datetime import datetime

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves")


# ── Item registry (built once on first use) ──────────────────────────────────

_ITEM_REGISTRY = None

def _get_registry():
    global _ITEM_REGISTRY
    if _ITEM_REGISTRY is not None:
        return _ITEM_REGISTRY
    from .items import (WEAPONS, ARMORS, CONSUMABLES, SKILL_BOOKS,
                        STARTING_WEAPONS, ARTIFACT_ARMORS)
    all_items = WEAPONS + ARMORS + CONSUMABLES + SKILL_BOOKS + STARTING_WEAPONS + ARTIFACT_ARMORS
    _ITEM_REGISTRY = {item.name: item for item in all_items}
    return _ITEM_REGISTRY


def _item_to_dict(item):
    """Minimal representation — just enough to look it up on load."""
    if item is None:
        return None
    return {"name": item.name, "itype": item.itype}


def _item_from_dict(d):
    if d is None:
        return None
    reg = _get_registry()
    return reg.get(d["name"])


# ── Serialization ─────────────────────────────────────────────────────────────

def player_to_dict(player):
    equipment = {}
    for slot, item in player.equipment.items():
        equipment[slot] = _item_to_dict(item)

    inventory = [_item_to_dict(i) for i in player.inventory]

    return {
        "name":          player.name,
        "cls_name":      player.cls_name,
        "level":         player.level,
        "xp":            player.xp,
        "xp_next":       player.xp_next,
        "stat_points":   player.stat_points,
        "gold":          player.gold,
        "hp":            player.hp,
        "mp":            player.mp,
        "strength":      player.strength,
        "intelligence":  player.intelligence,
        "agility":       player.agility,
        "vitality":      player.vitality,
        "luck":          player.luck,
        "perception":    player.perception,
        "skills":        list(player.skills),
        "killed_bosses": list(player.killed_bosses),
        "visited_zones": list(player.visited_zones),
        "status_effects":list(player.status_effects),
        "equipment":     equipment,
        "inventory":     inventory,
        "saved_at":      datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def player_from_dict(d):
    from .character import Character
    player = Character(d["name"], d["cls_name"])

    player.level        = d["level"]
    player.xp           = d["xp"]
    player.xp_next      = d["xp_next"]
    player.stat_points  = d["stat_points"]
    player.gold         = d["gold"]
    player.strength     = d["strength"]
    player.intelligence = d["intelligence"]
    player.agility      = d["agility"]
    player.vitality     = d["vitality"]
    player.luck         = d["luck"]
    player.perception   = d["perception"]
    player.skills       = d["skills"]
    player.killed_bosses = set(d["killed_bosses"])
    player.visited_zones = set(d["visited_zones"])
    player.status_effects = d["status_effects"]

    for slot, idict in d["equipment"].items():
        player.equipment[slot] = _item_from_dict(idict)

    player.inventory = [i for i in (_item_from_dict(x) for x in d["inventory"]) if i is not None]

    player._recalc_max()
    player.hp = d["hp"]
    player.mp = d["mp"]

    return player


# ── File I/O ──────────────────────────────────────────────────────────────────

def _save_path(player_name):
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in player_name)
    return os.path.join(SAVE_DIR, f"{safe}.json")


def save_game(player):
    """Serialize player to JSON in saves/. Returns (True, path) or (False, error)."""
    os.makedirs(SAVE_DIR, exist_ok=True)
    path = _save_path(player.name)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(player_to_dict(player), f, indent=2)
        return True, path
    except Exception as e:
        return False, str(e)


def load_game(path):
    """Deserialize a player from a save file. Returns player or raises."""
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    return player_from_dict(d)


def list_saves():
    """Return list of dicts with save metadata, sorted newest first."""
    if not os.path.isdir(SAVE_DIR):
        return []
    saves = []
    for fname in os.listdir(SAVE_DIR):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(SAVE_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            saves.append({
                "path":    path,
                "name":    d.get("name", "Unknown"),
                "cls":     d.get("cls_name", "?"),
                "level":   d.get("level", 1),
                "gold":    d.get("gold", 0),
                "saved_at":d.get("saved_at", ""),
            })
        except Exception:
            continue
    saves.sort(key=lambda s: s["saved_at"], reverse=True)
    return saves
