"""
World exploration: zones, events, loot, merchants, shrines.
"""
import random
from .ui import clear, header, slow_print, menu, pause, color, divider, hp_bar
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

ZONE_ROOMS = {
    "Mossy Ruins": [
        "You step through a collapsed archway. Ferns push through the cracked flagstones.",
        "A long hall stretches ahead, its ceiling open to the grey sky.",
        "A flooded chamber — your boots splash through ankle-deep rainwater.",
        "Carved stone faces line the walls, their expressions worn smooth by centuries.",
        "You squeeze through a narrow gap where two walls have folded together.",
        "A central courtyard, open and eerily still. Moss covers everything.",
    ],
    "Goblin Warrens": [
        "A low tunnel reeks of rot and old cook-fires.",
        "A wider chamber. Crude cots line the walls — recently abandoned.",
        "The floor is sticky. You don't look down.",
        "A rickety rope bridge spans a pit of unknown depth.",
        "Scratched tally marks cover every surface. Someone was counting something.",
        "A collapsed section forces you to crawl. Your armour scrapes the rock.",
    ],
    "Haunted Forest": [
        "Fog hangs between the trees at chest height. Shapes drift through it.",
        "A ring of dead birds lies arranged in a perfect circle on the ground.",
        "The trees here grow in wrong directions — twisted back on themselves.",
        "A child's shoe sits in the middle of the path. Just one.",
        "The canopy closes overhead. No light filters through.",
        "Distant laughter echoes, then cuts off abruptly.",
    ],
    "Bandit Stronghold": [
        "A makeshift gate of sharpened logs bars the next passage. You slip through a gap.",
        "Watch-fire embers still glow in a rusted brazier. The guards aren't far.",
        "A storage room packed with stolen crates and barrels.",
        "The main hall — long tables overturned, evidence of a recent brawl.",
        "A narrow catwalk above a training yard. Below, figures spar in torchlight.",
        "A heavy iron door stands ajar. The warden's quarters.",
    ],
    "Sunken Catacombs": [
        "Black water rises to your knees. Something brushes past your leg.",
        "Rows of stone sarcophagi, their lids cracked open from within.",
        "A vaulted chamber where the ceiling drips constantly into the dark water below.",
        "Carved epitaphs line the walls — names you don't recognise. Then one you do.",
        "A narrow staircase spirals further down into the flooded dark.",
        "An altar, still dry on a raised plinth. Offerings rot on its surface.",
    ],
    "Ashwood Wastes": [
        "Charred trunks surround you like black pillars. Nothing grows here.",
        "A crater where something enormous landed and burned.",
        "The ash is ankle-deep. Every step leaves a perfect print behind you.",
        "Smoke rises from fissures in the earth. The ground is warm underfoot.",
        "The skeleton of a building — walls standing, everything inside incinerated.",
        "A twisted iron sculpture. You realise it used to be a gate.",
    ],
    "Venom Hollows": [
        "Thick webbing coats the walls. It trembles without wind.",
        "Egg sacs the size of barrels hang from the ceiling.",
        "The tunnel narrows. Something has been dragging prey along the floor — recently.",
        "A chamber where the air shimmers with a faint toxic haze.",
        "A dried husk in armour, suspended in webbing. Its weapons are still good.",
        "The floor here is slick with old venom. You move carefully.",
    ],
    "Ironvault Depths": [
        "Rusted gears the size of cart wheels grind slowly overhead.",
        "A conveyor belt still moves, carrying nothing to nowhere.",
        "The walls here are solid iron plate, riveted together by long-dead hands.",
        "A control room full of levers, all seized with rust.",
        "Steam vents periodically through cracks in the floor. Time your steps.",
        "A vast chamber where the machinery is densest — and loudest.",
    ],
    "Rift Borderlands": [
        "The air tears open and seals again as you watch.",
        "Gravity shifts slightly — you adjust your footing and press on.",
        "A stretch of ground that isn't quite there. You cross carefully.",
        "Two versions of the same rock occupy the same space, flickering between each other.",
        "A creature from elsewhere drifts past, ignoring you entirely.",
        "The sky here is the wrong colour. You've stopped asking why.",
    ],
    "The Shattered Expanse": [
        "A floating island of rock. You jump across a gap with nothing below.",
        "Chains the size of houses connect two distant landmasses. You walk one.",
        "A waterfall that falls upward, spraying mist across your path.",
        "The remnant of a building drifts slowly past at eye level.",
        "Gravity has a clear direction here — it just isn't down.",
        "You reach a wide platform. The abyss surrounds you on all sides.",
    ],
    "The Sovereign's Sanctum": [
        "The walls pulse with void light. Your vision swims.",
        "Pillars of solidified rift energy line a grand corridor.",
        "The floor is transparent. Infinite darkness churns beneath it.",
        "Whispers form words in a language you almost understand.",
        "An antechamber. Beyond the sealed door, something immense waits.",
        "The air here hums at a frequency that vibrates your teeth.",
    ],
}


def explore(player):
    """Main exploration loop — player-driven depth system."""
    available = [z for z in ZONES if player.level >= z["min_level"]]
    zone_names = [f"{z['name']} (Lv.{z['min_level']}+)" for z in available]
    zone_names.append("Return to camp")

    idx = menu(zone_names, title="Choose a Zone")
    if idx == len(available):
        return

    zone = available[idx]
    player.visited_zones.add(zone["name"])

    clear()
    header(f"Entering: {zone['name']}")
    slow_print(f"\n  {zone['description']}\n")
    pause()

    depth = 0
    campfire_uses = 2
    boss_fought = False
    room_index = 0
    just_rested = False

    while player.is_alive():

        if not just_rested:
            # Room flavour
            room_pool = ZONE_ROOMS.get(zone["name"], [])
            if room_pool:
                slow_print(f"\n  {room_pool[room_index % len(room_pool)]}")
                room_index += 1
            pause()

            # Boss gate at depth 5+, otherwise normal event
            if depth >= 5 and not boss_fought:
                boss_data = get_available_boss(player.level, player.killed_bosses)
                if boss_data:
                    _combat_event(player, zone, force_boss=True)
                    boss_fought = True
                else:
                    event = _roll_event(zone, depth)
                    campfire_uses = _run_event(player, zone, event, depth, campfire_uses)
            else:
                event = _roll_event(zone, depth)
                campfire_uses = _run_event(player, zone, event, depth, campfire_uses)

        just_rested = False

        if not player.is_alive():
            slow_print(color("\n  You have been defeated...", "red"))
            return

        _show_expedition_status(player, depth, campfire_uses, zone)

        choices = ["Press Deeper"]
        if campfire_uses > 0:
            choices.append(f"Make Camp ({campfire_uses} use(s) left)")
        else:
            choices.append("Make Camp (no supplies left)")
        choices.append("Return to Camp")

        choice_idx = menu(choices, title="What do you do?")

        if choice_idx == 0:
            depth += 1

        elif choice_idx == 1:
            if campfire_uses > 0:
                campfire_uses = _campfire_rest(player, zone, campfire_uses)
                just_rested = True
            else:
                slow_print("\n  You have no campfire supplies left.")
                pause()
                just_rested = True

        else:
            break

    slow_print("\n  You make it back to camp safely.")
    pause()


def _show_expedition_status(player, depth, campfire_uses, zone):
    clear()
    divider()
    print(f"  Zone  : {color(zone['name'], 'cyan')}   Depth : {color(str(depth), 'yellow')}")
    print(f"  HP    : {hp_bar(player.hp, player.max_hp)}")
    print(f"  MP    : {hp_bar(player.mp, player.max_mp)}")
    if player.status_effects:
        effects_str = ", ".join(player.status_effects)
        print(f"  {color('Status: ' + effects_str, 'red')}")
    uses_color = "green" if campfire_uses > 0 else "dim"
    print(f"  {color(f'Campfire uses: {campfire_uses}/2', uses_color)}")
    divider()


def _roll_event(zone, depth):
    zone_shift = int(zone["danger"] * 20)
    weights = dict(EVENT_WEIGHTS)
    weights["combat"]   += zone_shift + depth * 5
    weights["loot"]     += depth * 3
    weights["merchant"]  = max(2, weights["merchant"] - max(0, depth - 2) * 3)
    weights["rest"]      = max(1, weights["rest"] - zone_shift // 2 - depth * 2)
    events = list(weights.keys())
    wts    = list(weights.values())
    return random.choices(events, weights=wts, k=1)[0]


def _run_event(player, zone, event, depth, campfire_uses_remaining):
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
        campfire_uses_remaining = _rest_event(player, zone, campfire_uses_remaining)
    return campfire_uses_remaining


# ── Events ───────────────────────────────────────────────────────────────────

def _combat_event(player, zone, force_boss=False):
    boss_data = None
    if force_boss:
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
        player.hp = 1
        lost = min(player.gold, random.randint(5, max(5, player.gold // 4)))
        player.gold -= lost
        slow_print(f"  You lost {lost} gold while fleeing for your life.")
        pause()


def _campfire_rest(player, zone, campfire_uses_remaining):
    clear()
    header("Making Camp")
    campfire_art = [
        "      ( )",
        "   (  ) )",
        "   ) _  (",
        "  (_/ \\_ )",
        "  /|  |\\",
        " / |  | \\",
    ]
    for line in campfire_art:
        print(f"  {color(line, 'yellow')}")
    slow_print("\n  You scrape together kindling and coax a small fire to life.")
    slow_print("  The warmth creeps back into your bones.\n")

    hp_gain = int(player.max_hp * 0.50)
    mp_gain = int(player.max_mp * 0.50)
    player.hp = min(player.max_hp, player.hp + hp_gain)
    player.mp = min(player.max_mp, player.mp + mp_gain)
    slow_print(f"  Restored {hp_gain} HP and {mp_gain} MP.")

    if player.status_effects:
        cleared = next(iter(player.status_effects))
        player.status_effects.discard(cleared)
        slow_print(f"  The rest helps clear your {cleared} status.")

    if random.random() < 0.25:
        slow_print(color("\n  The firelight attracts attention! Something approaches!", "red"))
        pause()
        _combat_event(player, zone)
    else:
        rest_flavour = [
            "  The fire pops and settles. For a moment, all is quiet.",
            "  Somewhere distant, water drips. You close your eyes briefly.",
            "  The flames die down. You feel steadier.",
            "  No sound but the fire. You take what peace you can.",
        ]
        slow_print(random.choice(rest_flavour))

    pause()
    return campfire_uses_remaining - 1


def _rest_event(player, zone, campfire_uses_remaining):
    """Player stumbles upon an abandoned campfire — free rest, no use consumed."""
    clear()
    header("Abandoned Campfire")
    slow_print("\n  A cold campfire smoulders in a sheltered corner — someone was here recently.")
    slow_print("  The embers still hold a little warmth. You fan them back to life.")
    pause()
    # Pass uses+1 so _campfire_rest's decrement nets to zero change
    _campfire_rest(player, zone, campfire_uses_remaining + 1)
    return campfire_uses_remaining


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
