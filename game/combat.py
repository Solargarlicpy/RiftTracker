"""
Turn-based combat engine.
"""
import random
from .ui import clear, header, divider, slow_print, menu, pause, hp_bar, color
from .skills import execute_skill, SKILLS
from .stats import crit_multiplier


def run_combat(player, enemy):
    """
    Run a full combat sequence.
    Returns: "win" | "lose" | "fled"
    """
    clear()
    header(f"⚔  COMBAT: {player.name} vs {enemy.name}")
    print(f"\n  {enemy.description}\n")
    pause()

    # Determine turn order
    player_first = player.get_initiative() >= enemy.agility + enemy.perception if hasattr(enemy, 'perception') else player.get_initiative() >= enemy.agility

    round_num = 0
    result = "lose"

    while player.is_alive() and enemy.is_alive():
        round_num += 1
        clear()
        _draw_hud(player, enemy, round_num)

        if player_first:
            cont = _player_turn(player, enemy)
            if cont == "fled":
                return "fled"
            if not enemy.is_alive():
                result = "win"
                break
            _enemy_turn(enemy, player)
            if not player.is_alive():
                result = "lose"
                break
        else:
            _enemy_turn(enemy, player)
            if not player.is_alive():
                result = "lose"
                break
            cont = _player_turn(player, enemy)
            if cont == "fled":
                return "fled"
            if not enemy.is_alive():
                result = "win"
                break

        player.tick_cooldowns()

    clear()
    if result == "win":
        _victory_screen(player, enemy)
    else:
        _defeat_screen(player, enemy)
    return result


# ── HUD ─────────────────────────────────────────────────────────────────────

def _draw_hud(player, enemy, round_num):
    print(f"\n{'═'*60}")
    print(f"  Round {round_num}".ljust(30) + f"  {enemy.name} (Lv.{enemy.level})".rjust(28))
    print(f"{'─'*60}")

    php = hp_bar(player.hp, player.max_hp)
    ehp = hp_bar(enemy.hp, enemy.max_hp)
    print(f"  {player.name} HP: {php}")
    print(f"  {enemy.name} HP: {ehp}")
    print(f"  MP: {player.mp}/{player.max_mp}", end="")

    fx = player.status_effects + list(player.temp_buffs.keys())
    if fx:
        print(f"  [{', '.join(fx)}]", end="")
    print()

    efx = enemy.status_effects
    if efx:
        print(f"  {enemy.name}: [{', '.join(efx)}]")
    print(f"{'═'*60}")


# ── Player turn ──────────────────────────────────────────────────────────────

def _player_turn(player, enemy):
    # Tick status effects
    for msg in player.tick_effects():
        slow_print(f"  {msg}")
    if not player.is_alive():
        return "dead"

    if "stunned" in player.status_effects:
        slow_print(f"  {player.name} is stunned and cannot act!")
        return "ok"

    options = ["Attack", "Skills", "Use Item", "Flee"]
    choice = menu(options, title="Your Turn")

    if choice == 0:  # Basic attack
        _player_attack(player, enemy)

    elif choice == 1:  # Skills
        result = _skill_menu(player, enemy)
        if result == "back":
            return _player_turn(player, enemy)

    elif choice == 2:  # Use item
        result = _item_menu(player)
        if result == "back":
            return _player_turn(player, enemy)

    elif choice == 3:  # Flee
        flee_chance = 0.40 + player.get_stat("agility") * 0.01
        if random.random() < flee_chance:
            slow_print(f"\n  {player.name} successfully fled!")
            pause()
            return "fled"
        else:
            slow_print(f"\n  {player.name} couldn't escape!")

    return "ok"


def _player_attack(player, enemy):
    import random
    atk = player.get_attack_damage()
    weapon = player.equipment.get("weapon")
    dtype = weapon.damage_type if weapon else "physical"

    # Crit check
    crit = random.random() < player.get_crit()
    if crit:
        atk = int(atk * crit_multiplier())

    defense = enemy.get_defense(dtype)
    dmg = max(1, atk - int(defense * 0.5))

    enemy.hp = max(0, enemy.hp - dmg)
    crit_str = color(" CRITICAL HIT!", "yellow") if crit else ""
    wname = weapon.name if weapon else "fists"
    slow_print(f"\n  {player.name} attacks with {wname} for {color(str(dmg), 'red')} damage!{crit_str}")


def _skill_menu(player, enemy):
    if not player.skills:
        slow_print("  You haven't learned any skills yet.")
        pause()
        return "back"

    opts = []
    for sk_name in player.skills:
        sk = SKILLS.get(sk_name, {})
        cd = player.skill_cooldowns.get(sk_name, 0)
        mp_cost = sk.get("mp_cost", 0)
        cd_str = f" [CD:{cd}]" if cd > 0 else ""
        mp_str = f" (MP:{mp_cost})"
        opts.append(f"{sk_name}{mp_str}{cd_str} — {sk.get('description','')}")
    opts.append("Back")

    idx = menu(opts, title="Skills")
    if idx == len(player.skills):
        return "back"

    sk_name = player.skills[idx]
    cd = player.skill_cooldowns.get(sk_name, 0)
    if cd > 0:
        slow_print(f"  {sk_name} is on cooldown for {cd} more turn(s).")
        pause()
        return "back"

    dmg, mp_used, msg, effects = execute_skill(sk_name, player, enemy)
    slow_print(f"\n  {msg}")

    if dmg > 0:
        enemy.hp = max(0, enemy.hp - dmg)

    for effect, value in effects.items():
        if effect in ("buff_str", "evasion", "shadow_step"):
            player.apply_effect(effect, value)
        else:
            if enemy.apply_effect(effect, value) is False:
                slow_print(f"  {enemy.name} is immune to {effect}!")

    sk = SKILLS.get(sk_name, {})
    cd_val = sk.get("cooldown", 0)
    if cd_val > 0:
        player.skill_cooldowns[sk_name] = cd_val

    return "ok"


def _item_menu(player):
    usables = [(i, item) for i, item in enumerate(player.inventory)
               if item.itype in ("consumable", "book")]
    if not usables:
        slow_print("  No usable items in inventory.")
        pause()
        return "back"

    opts = [f"{item.name} — {item.description}" for _, item in usables]
    opts.append("Back")
    idx = menu(opts, title="Use Item")
    if idx == len(usables):
        return "back"

    inv_idx, _ = usables[idx]
    ok, msg = player.use_item(inv_idx)
    slow_print(f"\n  {msg}")
    pause()
    return "ok"


# ── Enemy turn ───────────────────────────────────────────────────────────────

def _enemy_turn(enemy, player):
    for msg in enemy.tick_effects():
        slow_print(f"  {msg}")
    if not enemy.is_alive():
        return

    if "stunned" in enemy.status_effects:
        slow_print(f"\n  {enemy.name} is stunned and cannot act!")
        return

    atk = enemy.choose_attack()
    mp_cost = atk.get("mp_cost", 0)
    if mp_cost:
        enemy.mp = max(0, enemy.mp - mp_cost)

    # Player shadow step
    if player.shadow_step_active:
        player.shadow_step_active = False
        slow_print(f"\n  {enemy.name} uses {atk['name']}... but {player.name} phases through it!")
        return

    # Player dodge
    if random.random() < player.get_dodge():
        slow_print(f"\n  {enemy.name} uses {atk['name']}... {player.name} dodges!")
        return

    dmg_raw = atk["damage"]
    defense = player.get_defense(atk.get("type", "physical"))
    dmg = max(1, dmg_raw - int(defense * 0.5))
    player.hp = max(0, player.hp - dmg)

    slow_print(f"\n  {enemy.name} uses {color(atk['name'], 'cyan')} for {color(str(dmg), 'red')} damage!")

    # Apply effects to player
    effect = atk.get("effect")
    if effect:
        player.apply_effect(effect)
        slow_print(f"  {player.name} is {effect}!")

    pause()


# ── End screens ──────────────────────────────────────────────────────────────

def _victory_screen(player, enemy):
    header(f"  VICTORY! {enemy.name} defeated!")
    gold = enemy.gold_drop()
    player.gold += gold
    slow_print(f"\n  Looted {gold} gold from {enemy.name}.")


def _defeat_screen(player, enemy):
    header("  DEFEAT...")
    slow_print(f"\n  {player.name} was slain by {enemy.name}.")
    slow_print("  The world fades to black...")
    pause()
