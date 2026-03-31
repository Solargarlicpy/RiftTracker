"""
World exploration: zones, events, loot, merchants, shrines.
"""
import random
from .ui import clear, header, slow_print, menu, pause, color, divider
from .combat import run_combat
from .enemies import get_enemy_for_level, get_available_boss
from .items import loot_table, boss_loot_table, CONSUMABLES, WEAPONS, ARMORS, SKILL_BOOKS


ZONES = [
    {
        "name":        "Mossy Ruins",
        "min_level":   1,
        "description": "Crumbling stone walls covered in thick moss. Something rustles in the shadows.",
        "danger":      0.35,
    },
    {
        "name":        "Goblin Warrens",
        "min_level":   2,
        "description": "A maze of dank tunnels reeking of goblin musk.",
        "danger":      0.45,
    },
    {
        "name":        "Haunted Forest",
        "min_level":   4,
        "description": "Gnarled trees that seem to watch you. Strange lights drift between the trunks.",
        "danger":      0.50,
    },
    {
        "name":        "Bandit Stronghold",
        "min_level":   6,
        "description": "A fortified camp of ruthless outlaws.",
        "danger":      0.55,
    },
    {
        "name":        "Sunken Catacombs",
        "min_level":   8,
        "description": "Ancient burial chambers flooded with knee-deep black water.",
        "danger":      0.60,
    },
    {
        "name":        "Ashwood Wastes",
        "min_level":   9,
        "description": "A scorched expanse of dead trees and smouldering earth. Ashren's passage left nothing alive here.",
        "danger":      0.62,
    },
    {
        "name":        "Venom Hollows",
        "min_level":   10,
        "description": "A labyrinth of tunnels coated in dried webbing and old venom. The air is thick and wrong.",
        "danger":      0.65,
    },
    {
        "name":        "Ironvault Depths",
        "min_level":   11,
        "description": "The lowest chambers beneath the Iron Bulwark's domain. Rusted machinery still grinds in the dark.",
        "danger":      0.68,
    },
    {
        "name":        "Rift Borderlands",
        "min_level":   12,
        "description": "Reality shimmers and tears here. Creatures from another dimension roam freely.",
        "danger":      0.75,
    },
    {
        "name":        "The Shattered Expanse",
        "min_level":   13,
        "description": "Floating islands of rock drift over an abyss with no bottom. The laws of the world do not apply here.",
        "danger":      0.78,
    },
    {
        "name":        "The Sovereign's Sanctum",
        "min_level":   15,
        "description": "The heart of the rift itself. Every surface hums with void energy. Nothing survives here for long.",
        "danger":      0.85,
    },
]

EVENT_WEIGHTS = {
    "combat":   45,
    "loot":     20,
    "merchant": 12,
    "shrine":   8,
    "book":     8,
    "rest":     7,
}


def explore(player):
    """Main exploration loop for one zone visit."""
    available = [z for z in ZONES if player.level >= z["min_level"]]
    zone_names = [f"{z['name']} (Lv.{z['min_level']}+)" for z in available]
    zone_names.append("Return to camp")

    idx = menu(zone_names, title="Choose a Zone")
    if idx == len(available):
        return

    zone = available[idx]
    player.visited_zones.add(zone["name"])
    clear()
    header(f"Exploring: {zone['name']}")
    slow_print(f"\n  {zone['description']}\n")

    steps = random.randint(3, 6)
    for step in range(steps):
        if not player.is_alive():
            break
        slow_print(f"\n  You press deeper... (step {step+1}/{steps})")
        pause()
        event = _roll_event(zone)
        _run_event(player, zone, event)
        if not player.is_alive():
            return

    slow_print("\n  You make it back to camp safely.")
    pause()


def _roll_event(zone):
    danger_shift = int(zone["danger"] * 20)
    weights = dict(EVENT_WEIGHTS)
    weights["combat"] += danger_shift
    weights["rest"]   = max(2, weights["rest"] - danger_shift // 2)
    events = list(weights.keys())
    wts    = list(weights.values())
    return random.choices(events, weights=wts, k=1)[0]


def _run_event(player, zone, event):
    if event == "combat":
        _combat_event(player, zone)
    elif event == "loot":
        _loot_event(player)
    elif event == "merchant":
        _merchant_event(player)
    elif event == "shrine":
        _shrine_event(player)
    elif event == "book":
        _book_event(player)
    elif event == "rest":
        _rest_event(player)


# ── Events ───────────────────────────────────────────────────────────────────

def _combat_event(player, zone):
    # Boss encounter check (10% when any boss is eligible)
    boss_data = None
    if random.random() < 0.10:
        boss_data = get_available_boss(player.level, player.killed_bosses)

    if boss_data:
        enemy = boss_data["enemy"].scale_to_level(player.level)
        slow_print(color(f"\n  {boss_data['announcement']}", "red"))
        pause()
    else:
        enemy = get_enemy_for_level(player.level)
        slow_print(f"\n  A {color(enemy.name, 'red')} leaps from the shadows!")
        pause()

    result = run_combat(player, enemy)

    if result == "win":
        xp = enemy.xp_reward
        levels = player.gain_xp(xp)
        slow_print(f"\n  Gained {xp} XP!")
        if levels:
            for _ in range(levels):
                slow_print(color(f"\n  ★ LEVEL UP! Now level {player.level}! ★", "yellow"))
                slow_print(f"  HP and MP fully restored.")
                slow_print(f"  You have {player.stat_points} stat point(s) to spend.")

        if boss_data:
            # Boss-specific artifact loot
            first_kill = enemy.name not in player.killed_bosses
            player.killed_bosses.add(enemy.name)
            artifacts = boss_loot_table(enemy.name, first_kill)
            if artifacts:
                slow_print(color("\n  ★ BOSS LOOT ★", "yellow"))
                for item in artifacts:
                    ok, msg = player.pick_up(item)
                    if ok:
                        slow_print(f"  {color('ARTIFACT:', 'red')} {color(str(item), 'red')}")
                    else:
                        slow_print(f"  {msg} Left behind: {item.name}")

        # Always roll normal loot after any combat win (boss or not)
        drops = loot_table(player.level, player.get_loot_bonus())
        for item in drops:
            ok, msg = player.pick_up(item)
            if ok:
                slow_print(f"  Found: {color(str(item), 'cyan')}")
            else:
                slow_print(f"  {msg} Left behind: {item.name}")
        pause()

    elif result == "lose":
        slow_print(color("\n  You have been defeated...", "red"))
        player.hp = 1  # survive with 1 HP (permadeath opt-out)
        # Lose some gold
        lost = min(player.gold, random.randint(5, max(5, player.gold // 4)))
        player.gold -= lost
        slow_print(f"  You lost {lost} gold while fleeing for your life.")
        pause()


def _loot_event(player):
    clear()
    header("Treasure Found!")
    descriptions = [
        "You pry open a moss-covered chest.",
        "Beneath a pile of bones you discover a hidden cache.",
        "A glimmering object catches your eye in the rubble.",
        "You find an abandoned adventurer's pack.",
        "A secret compartment reveals itself in the wall.",
    ]
    slow_print(f"\n  {random.choice(descriptions)}")
    drops = loot_table(player.level, player.get_loot_bonus())
    gold = random.randint(max(2, player.level * 2), max(15, player.level * 8 + 5))
    player.gold += gold
    slow_print(f"  Found {gold} gold!")
    for item in drops:
        ok, msg = player.pick_up(item)
        if ok:
            slow_print(f"  Found: {color(str(item), 'cyan')}")
        else:
            slow_print(f"  {msg} Left behind: {item.name}")
    pause()


def _merchant_event(player):
    clear()
    header("Wandering Merchant")
    slow_print("\n  A hooded merchant steps from behind a tree.\n  \"Psst... care to browse my wares?\"")
    pause()

    # Generate a small stock of items
    stock = random.sample(CONSUMABLES, k=min(4, len(CONSUMABLES)))
    if player.level >= 3:
        stock += random.sample(WEAPONS + ARMORS, k=min(3, len(WEAPONS + ARMORS)))

    while True:
        clear()
        header("Merchant's Wares")
        slow_print(f"  Your gold: {player.gold}g\n")
        opts = [f"{item.name} [{item.rarity}] — {item.value}g" for item in stock]
        opts.append("Leave")
        idx = menu(opts)
        if idx == len(stock):
            slow_print("  \"Safe travels, adventurer.\"")
            pause()
            break
        item = stock[idx]
        if player.gold < item.value:
            slow_print("  Not enough gold!")
        else:
            ok, msg = player.pick_up(item)
            if ok:
                player.gold -= item.value
                slow_print(f"  Purchased {item.name} for {item.value}g.")
                stock.pop(idx)
            else:
                slow_print(f"  {msg}")
        pause()


def _shrine_event(player):
    clear()
    header("Ancient Shrine")
    shrines = [
        ("Shrine of Vitality", "vitality", 1,
         "The stone pulses with warm light. You feel more resilient."),
        ("Shrine of Power", "strength", 1,
         "Runes flare red. Your muscles surge with new might."),
        ("Shrine of Arcana", "intelligence", 1,
         "Blue flames dance across the altar. Your mind sharpens."),
        ("Shrine of the Wind", "agility", 1,
         "A gust circles you. Your movements quicken."),
        ("Shrine of Fortune", "luck", 1,
         "Golden light showers you. Fate smiles upon you."),
        ("Shrine of Sight", "perception", 1,
         "Your eyes open wider. Nothing escapes your notice now."),
        ("Healing Font", None, None,
         "Clear water bubbles from the ground. You drink deeply."),
    ]
    s = random.choice(shrines)
    slow_print(f"\n  You discover the {s[0]}.")
    slow_print(f"  {s[3]}")
    if s[1]:
        setattr(player, s[1], getattr(player, s[1]) + s[2])
        player._recalc_max()
        slow_print(f"  {s[1].capitalize()} permanently +{s[2]}!")
    else:
        player.hp = player.max_hp
        player.mp = player.max_mp
        slow_print("  HP and MP fully restored!")
    pause()


def _book_event(player):
    clear()
    header("Dusty Tome")
    slow_print("\n  Half-buried in the rubble you find an ancient book.")
    book = random.choice(SKILL_BOOKS)
    ok, msg = player.pick_up(book)
    if ok:
        slow_print(f"  You pick up: {color(str(book), 'cyan')}")
        slow_print(f"  \"{book.description}\"")
    else:
        slow_print(f"  {msg}")
    pause()


def _rest_event(player):
    clear()
    header("A Quiet Moment")
    descs = [
        "You find a sheltered alcove and take a short rest.",
        "A warm campfire still smoulders — someone was here recently.",
        "You sit by a babbling brook and tend your wounds.",
        "A hidden grove offers a few minutes of peaceful calm.",
    ]
    slow_print(f"\n  {random.choice(descs)}")
    hp_gain = int(player.max_hp * 0.30)
    mp_gain = int(player.max_mp * 0.30)
    player.hp = min(player.max_hp, player.hp + hp_gain)
    player.mp = min(player.max_mp, player.mp + mp_gain)
    slow_print(f"  Restored {hp_gain} HP and {mp_gain} MP.")
    pause()
