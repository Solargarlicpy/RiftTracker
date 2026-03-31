"""
World Map screen — zones grouped by region with visited status,
danger bars, and boss indicators.
"""
from .ui import clear, header, pause, color, divider
from .world import ZONES

REGIONS = [
    {"name": "THE FRONTIER", "range": "Lv 1-6",   "color": "cyan",    "start": 0, "end": 4},
    {"name": "THE DEEP",     "range": "Lv 8-11",  "color": "yellow",  "start": 4, "end": 8},
    {"name": "THE RIFT",     "range": "Lv 12-15", "color": "magenta", "start": 8, "end": 11},
]

BOSS_ZONES = {
    "Iron Bulwark":        "Ironvault Depths",
    "The Venom Matriarch": "Venom Hollows",
    "Ashren the Unburnt":  "Ashwood Wastes",
    "The Rift Sovereign":  "The Sovereign's Sanctum",
}
_ZONE_BOSS = {v: k for k, v in BOSS_ZONES.items()}


def _danger_bar(danger, width=8):
    filled = max(1, round((danger - 0.30) / 0.60 * width))
    filled = min(filled, width)
    bar = '\u2588' * filled + '\u2591' * (width - filled)
    c = 'green' if danger <= 0.45 else ('yellow' if danger <= 0.62 else 'red')
    return color(bar, c)


def _region_header(name, level_range, clr):
    label = f"  {name}  {level_range}  "
    dashes = '\u2500' * (58 - len(label))
    print(color(label + dashes, clr))


def _zone_row(zone, player):
    name     = zone["name"]
    level    = zone["min_level"]
    locked   = player.level < level
    visited  = name in player.visited_zones
    boss     = _ZONE_BOSS.get(name)

    if locked:
        hidden = ("??? " + "\u2500" * 10 + " ???")[:23].ljust(23)
        return color(f"  [?] {hidden} Lv??  \u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591", "dim")

    name_col  = name.ljust(23)
    level_col = str(level).ljust(2)
    bar       = _danger_bar(zone["danger"])

    if boss:
        killed = boss in player.killed_bosses
        boss_tag = color("[B]", "dim") if killed else color("[B]", "magenta")
    else:
        boss_tag = "   "

    if visited:
        glyph    = color("[*]", "bold")
        name_str = color(name_col, "bold")
    else:
        glyph    = "[ ]"
        name_str = name_col

    return f"  {glyph} {name_str} Lv{level_col}  {bar} {boss_tag}"


def show_world_map(player):
    clear()
    header("World Map")
    print(f"\n  {color('[*]', 'bold')} Visited  "
          f"[ ] Unexplored  "
          f"{color('[?]', 'dim')} Locked  "
          f"{color('[B]', 'magenta')} Boss")
    print()

    for region in REGIONS:
        _region_header(region["name"], region["range"], region["color"])
        for zone in ZONES[region["start"]:region["end"]]:
            print(_zone_row(zone, player))
        print()

    divider()
    print(f"  Zones visited : {len(player.visited_zones)}/{len(ZONES)}")
    slain = ", ".join(sorted(player.killed_bosses)) if player.killed_bosses else "none"
    print(f"  Bosses slain  : {slain}")
    print()
    pause()
