#!/usr/bin/env python3
"""
Rift Tracker — A Text-Based RPG
================================
Classes  : Warrior, Mage, Ranger
Stats    : Strength, Intelligence, Agility, Vitality, Luck, Perception
Features : XP leveling, skill books, loot drops, full inventory & equipment
"""

import sys
import os

# Allow running from any directory
sys.path.insert(0, os.path.dirname(__file__))

from game.ui       import clear, header, slow_print, menu, prompt, pause, color, divider
from game.character import Character
from game.stats     import CLASS_BASES
from game.items     import STARTING_WEAPONS
from game.world     import explore
from game.menus     import (character_screen, inventory_screen,
                            allocate_stats, skills_screen, rest_at_camp)


TITLE = r"""
  ██████╗ ██╗███████╗████████╗    ████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗
  ██╔══██╗██║██╔════╝╚══██╔══╝    ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
  ██████╔╝██║█████╗     ██║          ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
  ██╔══██╗██║██╔══╝     ██║          ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
  ██║  ██║██║██║        ██║          ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
  ╚═╝  ╚═╝╚═╝╚═╝        ╚═╝          ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
"""


def title_screen():
    clear()
    print(color(TITLE, "cyan"))
    print("  " + "─" * 58)
    print("  A dungeon-crawling RPG of stats, skills, and survival.")
    print("  " + "─" * 58)
    print()


def choose_class():
    classes = ["Warrior", "Mage", "Ranger"]
    clear()
    header("Choose Your Class")
    for cls in classes:
        cfg = CLASS_BASES[cls]
        print(f"\n  {cfg['symbol']}  {color(cls, 'bold')}")
        print(f"     {cfg['description']}")
        stats = (f"STR:{cfg['strength']} INT:{cfg['intelligence']} AGI:{cfg['agility']} "
                 f"VIT:{cfg['vitality']} LCK:{cfg['luck']} PER:{cfg['perception']}")
        print(f"     {color(stats,'dim')}")
        print(f"     HP:{cfg['hp']}  MP:{cfg['mp']}")

    divider()
    idx = menu([f"{CLASS_BASES[c]['symbol']} {c}" for c in classes], title="Your class")
    return classes[idx]


def choose_weapon():
    clear()
    header("Choose Your Starting Weapon")
    slow_print("  Every adventurer needs a weapon. Choose wisely.\n")

    for wpn in STARTING_WEAPONS:
        bonuses = ", ".join(f"{k.capitalize()}+{v}" for k, v in wpn.stat_bonus.items())
        bonus_str = f"  [{bonuses}]" if bonuses else ""
        print(f"  {color(wpn.name, 'bold')}  —  {wpn.damage} dmg ({wpn.damage_type}){bonus_str}")
        print(f"    {color(wpn.description, 'dim')}")
        print()

    divider()
    idx = menu([wpn.name for wpn in STARTING_WEAPONS], title="Your weapon")
    return STARTING_WEAPONS[idx]


def new_game():
    title_screen()
    slow_print("  The Rift tears open across the sky. Ancient creatures pour forth.")
    slow_print("  Only one hunter has the will to push back the darkness.\n")
    pause()

    cls_name = choose_class()
    clear()
    header(f"Create Your {cls_name}")
    name = ""
    while not name:
        name = prompt("  Enter your character's name: ")
        if not name:
            slow_print("  You must enter a name.")

    starting_weapon = choose_weapon()

    player = Character(name, cls_name)
    player.equipment["weapon"] = starting_weapon
    player._recalc_max()

    clear()
    header("Your Adventure Begins")
    slow_print(f"\n  {CLASS_BASES[cls_name]['symbol']}  {name}, the {cls_name}, steps into the Rift Borderlands.")
    slow_print(f"\n  Your stats:")
    for line in player.stat_block():
        slow_print(f"  {line}")
    slow_print("\n  Tip: Explore zones to find loot, skill books, and enemies.")
    slow_print("  Tip: Allocate stat points after leveling up in the Character menu.")
    pause()
    return player


def camp_menu(player):
    """Main hub between explorations."""
    while True:
        clear()
        header("Camp")
        # Quick status bar
        from game.ui import hp_bar, xp_bar
        print(f"\n  {player.name} [{player.cls_name}]  Lv.{player.level}  Gold: {player.gold}g")
        print(f"  HP  {hp_bar(player.hp, player.max_hp)}")
        print(f"  XP  {xp_bar(player.xp, player.xp_next)}")

        if player.stat_points > 0:
            print(color(f"\n  ★ {player.stat_points} stat point(s) ready to allocate!", "yellow"))
        if player.status_effects:
            print(color(f"  Status: {', '.join(player.status_effects)}", "red"))
        print()

        options = [
            "Explore",
            "Character Sheet",
            "Inventory",
            "Allocate Stats",
            "Skills",
            "Rest (restore HP/MP)",
            "Quit",
        ]
        choice = menu(options)

        if choice == 0:
            explore(player)
            if not player.is_alive():
                return False   # signal game over

        elif choice == 1:
            character_screen(player)

        elif choice == 2:
            inventory_screen(player)

        elif choice == 3:
            allocate_stats(player)

        elif choice == 4:
            skills_screen(player)

        elif choice == 5:
            rest_at_camp(player)

        elif choice == 6:
            if _confirm_quit():
                return True   # quit

    return True


def _confirm_quit():
    from game.ui import confirm
    return confirm("Are you sure you want to quit?")


def game_over(player):
    clear()
    print(color("\n\n  ☠  GAME OVER  ☠\n", "red"))
    slow_print(f"  {player.name} has fallen.")
    slow_print(f"  Final level: {player.level}")
    slow_print(f"  Gold remaining: {player.gold}g")
    pause()


def main():
    while True:
        title_screen()
        opts = ["New Game", "Quit"]
        choice = menu(opts)
        if choice == 1:
            clear()
            print("\n  May the Rift spare you, traveller.\n")
            break

        player = new_game()
        result = camp_menu(player)

        if not result:
            game_over(player)

        clear()
        again = menu(["Play Again", "Quit"], title="Thanks for playing!")
        if again == 1:
            break

    print()


if __name__ == "__main__":
    main()
