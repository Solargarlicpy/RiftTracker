"""
In-camp menus: character sheet, inventory, stat allocation, skills.
"""
from .ui import clear, header, slow_print, menu, pause, color, hp_bar, xp_bar, box, divider
from .items import SLOTS, RARITIES
from .skills import SKILLS


def character_screen(player):
    clear()
    cfg = __import__('game.stats', fromlist=['CLASS_BASES']).CLASS_BASES[player.cls_name]
    header(f"  {cfg['symbol']}  {player.name}  —  {player.cls_name}  (Lv. {player.level})")

    print(f"\n  HP  {hp_bar(player.hp, player.max_hp)}")
    print(f"  MP  {hp_bar(player.mp, player.max_mp, )}")
    print(f"  XP  {xp_bar(player.xp, player.xp_next)}")
    print(f"\n  Gold: {player.gold}g")
    divider()

    stats = ["strength","intelligence","agility","vitality","luck","perception"]
    stat_labels = {"strength":"STR","intelligence":"INT","agility":"AGI",
                   "vitality":"VIT","luck":"LCK","perception":"PER"}
    row = ""
    for i, s in enumerate(stats):
        base = getattr(player, s)
        total = player.get_stat(s)
        bonus = total - base
        bstr = f"+{bonus}" if bonus > 0 else (f"{bonus}" if bonus < 0 else "")
        row += f"  {stat_labels[s]}: {total:>3}{(' ('+bstr+')'if bstr else ''):6}"
        if (i+1) % 3 == 0:
            print(row)
            row = ""

    divider()
    print(f"  Dodge: {player.get_dodge()*100:.1f}%   "
          f"Crit: {player.get_crit()*100:.1f}%   "
          f"Atk: {player.get_attack_damage()}   "
          f"Def: {player.get_defense()}")

    if player.stat_points > 0:
        print(color(f"\n  ★ {player.stat_points} UNSPENT STAT POINT(S) — Go to Allocate Stats!", "yellow"))

    divider()
    print("\n  [Equipped Gear]")
    for slot in SLOTS:
        item = player.equipment.get(slot)
        iname = item.name if item else color("Empty", "dim")
        print(f"    {slot:<8}: {iname}")

    divider()
    pause()


def inventory_screen(player):
    while True:
        clear()
        header("Inventory")
        print(f"  Gold: {player.gold}g   Slots: {len(player.inventory)}/{player.max_inv}\n")

        if not player.inventory:
            slow_print("  Your pack is empty.")
            pause()
            return

        opts = []
        for item in player.inventory:
            rarity_color_map = {
                "Common":"dim","Uncommon":"green","Rare":"blue","Epic":"magenta",
                "Legendary":"yellow","Artifact":"red"
            }
            rc = rarity_color_map.get(item.rarity, "reset")
            tag = ""
            if item.itype == "weapon":
                tag = f" [WPN {item.damage} {item.damage_type}]"
            elif item.itype == "armor":
                tag = f" [ARM DEF:{item.defense} slot:{item.slot}]"
            elif item.itype == "consumable":
                tag = f" [USE]"
            elif item.itype == "book":
                tag = f" [BOOK: {item.skill_name}]"
            opts.append(color(f"{item.name} [{item.rarity}]", rc) + tag)
        opts.append("Back")

        idx = menu(opts, title="Select item")
        if idx == len(player.inventory):
            return

        item = player.inventory[idx]
        _item_action(player, idx, item)


def _item_action(player, idx, item):
    clear()
    header(f"  {item.name}")
    print(f"  Type    : {item.itype.capitalize()}")
    print(f"  Rarity  : {item.rarity}")
    print(f"  Value   : {item.value}g")
    if hasattr(item, 'description') and item.description:
        print(f"  Desc    : {item.description}")
    if hasattr(item, 'damage'):
        print(f"  Damage  : {item.damage} ({item.damage_type})")
    if hasattr(item, 'defense'):
        print(f"  Defense : {item.defense}  Slot: {item.slot}")
    if hasattr(item, 'stat_bonus') and item.stat_bonus:
        bonuses = ", ".join(f"{k}+{v}" for k, v in item.stat_bonus.items())
        print(f"  Bonuses : {bonuses}")
    print()

    actions = []
    if item.itype in ("weapon", "armor"):
        actions.append("Equip")
    if item.itype in ("consumable", "book"):
        actions.append("Use")
    actions += ["Drop", "Cancel"]

    choice = menu(actions)
    act = actions[choice]

    if act == "Equip":
        ok, msg = player.equip(idx)
        slow_print(f"  {msg}")
    elif act == "Use":
        ok, msg = player.use_item(idx)
        slow_print(f"  {msg}")
    elif act == "Drop":
        dropped = player.drop_item(idx)
        if dropped:
            slow_print(f"  Dropped {dropped.name}.")
    pause()


def allocate_stats(player):
    if player.stat_points == 0:
        slow_print("\n  No stat points to spend.")
        pause()
        return

    stats = ["strength", "intelligence", "agility", "vitality", "luck", "perception"]
    labels = {"strength":"Strength","intelligence":"Intelligence","agility":"Agility",
              "vitality":"Vitality","luck":"Luck","perception":"Perception"}
    descs  = {
        "strength":     "Increases physical damage and carry capacity.",
        "intelligence": "Increases magic damage and max MP.",
        "agility":      "Increases dodge, crit, and ranged damage.",
        "vitality":     "Increases max HP and resilience.",
        "luck":         "Improves crit, loot quality, and flee chance.",
        "perception":   "Increases initiative and ranged accuracy.",
    }

    while player.stat_points > 0:
        clear()
        header(f"Allocate Stats  [{player.stat_points} point(s) remaining]")
        opts = []
        for s in stats:
            base = getattr(player, s)
            total = player.get_stat(s)
            opts.append(f"{labels[s]:<14} {total:>3}  — {descs[s]}")
        opts.append("Done")
        idx = menu(opts)
        if idx == len(stats):
            break
        stat_name = stats[idx]
        ok = player.allocate_stat(stat_name)
        if ok:
            slow_print(f"  {labels[stat_name]} increased to {player.get_stat(stat_name)}!")
        pause()


def skills_screen(player):
    clear()
    header(f"{player.name}'s Skills")
    if not player.skills:
        slow_print("\n  You haven't learned any skills yet.")
        slow_print("  Find Skill Books in the world to unlock abilities.")
        pause()
        return

    for sk_name in player.skills:
        sk = SKILLS.get(sk_name, {})
        cd = player.skill_cooldowns.get(sk_name, 0)
        status = color(f"  [CD:{cd}]", "red") if cd > 0 else color("  [Ready]", "green")
        print(f"\n  {color(sk_name, 'cyan')}{status}")
        print(f"    MP Cost : {sk.get('mp_cost', 0)}")
        print(f"    Category: {sk.get('category','').capitalize()}")
        print(f"    {sk.get('description','')}")

    pause()


def rest_at_camp(player):
    clear()
    header("Rest at Camp")
    slow_print("\n  You settle down by the fire and rest for the night.")
    player.hp = player.max_hp
    player.mp = player.max_mp
    player.status_effects.clear()
    slow_print("  HP and MP fully restored. All status effects cleared.")
    pause()
