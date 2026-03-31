"""
Skill definitions and execution.
Skills are learned from books found during exploration/loot.
"""
import random

# Each skill: name -> {classes, mp_cost, description, effect_fn}
# effect_fn(attacker, defender, in_combat) -> (damage, message)

SKILLS = {
    "Power Strike": {
        "classes": ["Warrior"],
        "mp_cost": 10,
        "cooldown": 0,
        "description": "A mighty blow dealing 2.5x weapon damage.",
        "category": "offense",
    },
    "Whirlwind": {
        "classes": ["Warrior"],
        "mp_cost": 20,
        "cooldown": 3,
        "description": "Spin strike. Deals 2x damage and ignores some defense.",
        "category": "offense",
    },
    "Shield Bash": {
        "classes": ["Warrior"],
        "mp_cost": 8,
        "cooldown": 2,
        "description": "Bash with your shield. Stuns enemy for 1 turn.",
        "category": "control",
    },
    "Battle Cry": {
        "classes": ["Warrior"],
        "mp_cost": 15,
        "cooldown": 4,
        "description": "Boost STR by 5 for 3 turns.",
        "category": "buff",
    },
    "Fireball": {
        "classes": ["Mage"],
        "mp_cost": 18,
        "cooldown": 0,
        "description": "Hurl a fireball. INT-scaled magic damage.",
        "category": "offense",
    },
    "Ice Shard": {
        "classes": ["Mage"],
        "mp_cost": 12,
        "cooldown": 0,
        "description": "Ice projectile that slows the enemy (−3 AGI for 2 turns).",
        "category": "debuff",
    },
    "Arcane Blast": {
        "classes": ["Mage"],
        "mp_cost": 25,
        "cooldown": 2,
        "description": "Pure arcane energy. Ignores all armor.",
        "category": "offense",
    },
    "Mana Drain": {
        "classes": ["Mage"],
        "mp_cost": 15,
        "cooldown": 3,
        "description": "Siphon enemy life force, converting it to your MP.",
        "category": "utility",
    },
    "Rift Pulse": {
        "classes": ["Mage"],
        "mp_cost": 50,
        "cooldown": 5,
        "description": "Legendary arcane explosion. Massive INT-scaled damage.",
        "category": "offense",
    },
    "Steady Shot": {
        "classes": ["Ranger"],
        "mp_cost": 8,
        "cooldown": 0,
        "description": "Aimed shot dealing 2x ranged damage with high crit chance.",
        "category": "offense",
    },
    "Poison Arrow": {
        "classes": ["Ranger"],
        "mp_cost": 10,
        "cooldown": 0,
        "description": "Arrow coated in poison. Deals damage over 3 turns.",
        "category": "debuff",
    },
    "Evasion": {
        "classes": ["Ranger"],
        "mp_cost": 12,
        "cooldown": 3,
        "description": "Enter evasive stance. Dodge chance +40% for 1 turn.",
        "category": "buff",
    },
    "Shadow Step": {
        "classes": ["Ranger"],
        "mp_cost": 18,
        "cooldown": 4,
        "description": "Phase out briefly. Enemy's next attack misses.",
        "category": "utility",
    },
    "Thunder Clap": {
        "classes": ["Warrior", "Ranger"],
        "mp_cost": 30,
        "cooldown": 5,
        "description": "Thunderous strike. Stuns and deals heavy damage.",
        "category": "offense",
    },
}


def execute_skill(skill_name, attacker, defender):
    """
    Execute a skill in combat.
    Returns (damage_dealt, mp_used, message, effects_dict)
    effects_dict: {stun, slow, poison, buff_str, evasion, shadow_step, ...}
    """
    sk = SKILLS.get(skill_name)
    if not sk:
        return 0, 0, f"Unknown skill: {skill_name}", {}

    mp_cost = sk["mp_cost"]
    if attacker.mp < mp_cost:
        return 0, 0, f"Not enough MP! Need {mp_cost}, have {attacker.mp}.", {}

    attacker.mp -= mp_cost
    effects = {}
    msg = ""
    dmg = 0

    strength = attacker.get_stat("strength")
    intelligence = attacker.get_stat("intelligence")
    agility = attacker.get_stat("agility")

    weapon = attacker.equipment.get("weapon")
    wdmg = weapon.damage if weapon else 0
    dtype = weapon.damage_type if weapon else "physical"

    # ── Warrior ─────────────────────────────────────────────────────────────
    if skill_name == "Power Strike":
        raw = (strength * 2 + wdmg) * 2.5
        dmg = _apply_defense(raw, defender, "physical")
        msg = f"{attacker.name} uses Power Strike for {dmg} damage!"

    elif skill_name == "Whirlwind":
        raw = (strength * 2 + wdmg) * 2
        dmg = int(raw)   # ignores defense entirely
        msg = f"{attacker.name} spins in a Whirlwind for {dmg} damage! (ignores armor)"

    elif skill_name == "Shield Bash":
        raw = strength * 1.5
        dmg = _apply_defense(raw, defender, "physical")
        effects["stun"] = 1
        msg = f"{attacker.name} Shield Bashes for {dmg} damage! Enemy is stunned!"

    elif skill_name == "Battle Cry":
        effects["buff_str"] = 3  # 3 turns
        msg = f"{attacker.name} lets out a Battle Cry! STR +5 for 3 turns!"

    # ── Mage ─────────────────────────────────────────────────────────────────
    elif skill_name == "Fireball":
        raw = intelligence * 3 + wdmg * 1.5
        dmg = _apply_defense(raw, defender, "magic")
        msg = f"{attacker.name} launches a Fireball for {dmg} magic damage!"

    elif skill_name == "Ice Shard":
        raw = intelligence * 2 + wdmg
        dmg = _apply_defense(raw, defender, "magic")
        effects["slow"] = 2  # −3 AGI for 2 turns
        msg = f"{attacker.name} fires an Ice Shard for {dmg} damage! Enemy slowed!"

    elif skill_name == "Arcane Blast":
        dmg = int(intelligence * 4)   # ignores armor
        msg = f"{attacker.name} unleashes an Arcane Blast for {dmg} true magic damage!"

    elif skill_name == "Mana Drain":
        dmg_raw = intelligence * 2
        dmg = _apply_defense(dmg_raw, defender, "magic")
        gained_mp = min(dmg // 2, attacker.max_mp - attacker.mp)
        attacker.mp += gained_mp
        msg = f"{attacker.name} drains {dmg} life force! Gained {gained_mp} MP!"

    elif skill_name == "Rift Pulse":
        raw = intelligence * 6 + wdmg * 2
        dmg = int(raw)   # true damage
        msg = f"{attacker.name} detonates a RIFT PULSE for {dmg} devastating damage!"

    # ── Ranger ───────────────────────────────────────────────────────────────
    elif skill_name == "Steady Shot":
        crit = random.random() < (0.30 + attacker.get_stat("luck") * 0.02)
        raw = (agility * 1.5 + wdmg) * 2
        if crit:
            raw *= 1.75
        dmg = _apply_defense(raw, defender, "ranged")
        msg = f"{attacker.name} fires a Steady Shot for {dmg} damage!" + (" CRITICAL!" if crit else "")

    elif skill_name == "Poison Arrow":
        raw = agility + wdmg
        dmg = _apply_defense(raw, defender, "ranged")
        effects["poison"] = 3  # 3 turns
        msg = f"{attacker.name} fires a Poison Arrow for {dmg} damage! Enemy is poisoned!"

    elif skill_name == "Evasion":
        effects["evasion"] = 1  # +40% dodge for 1 turn
        msg = f"{attacker.name} enters Evasion stance! Dodge chance greatly increased!"

    elif skill_name == "Shadow Step":
        effects["shadow_step"] = 1  # negate next enemy attack
        msg = f"{attacker.name} uses Shadow Step! Next enemy attack will miss!"

    elif skill_name == "Thunder Clap":
        raw = (strength + agility) * 2 + wdmg * 2
        dmg = _apply_defense(raw, defender, "physical")
        effects["stun"] = 1
        msg = f"{attacker.name} smashes a Thunder Clap for {dmg} damage! Enemy stunned!"

    return dmg, mp_cost, msg, effects


def _apply_defense(raw_dmg, defender, dtype):
    defense = defender.get_defense(dtype)
    return max(1, int(raw_dmg - defense * 0.5))
