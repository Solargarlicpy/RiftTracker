"""
Core stat definitions and derived formulas.
Stats: Strength, Intelligence, Agility, Vitality, Luck, Perception
"""

BASE_STATS = {
    "strength":     0,
    "intelligence": 0,
    "agility":      0,
    "vitality":     0,
    "luck":         0,
    "perception":   0,
}

CLASS_BASES = {
    "Warrior": {
        "strength": 8, "intelligence": 2, "agility": 4,
        "vitality": 7, "luck": 3, "perception": 2,
        "hp": 120, "mp": 20,
        "stat_growth": {"strength": 3, "vitality": 2, "agility": 1, "intelligence": 1, "luck": 1, "perception": 1},
        "description": "A fierce melee fighter. High HP and Strength. Learns weapon mastery skills.",
        "symbol": "⚔",
    },
    "Mage": {
        "strength": 2, "intelligence": 9, "agility": 3,
        "vitality": 3, "luck": 4, "perception": 5,
        "hp": 60, "mp": 120,
        "stat_growth": {"intelligence": 3, "perception": 2, "agility": 1, "vitality": 1, "luck": 1, "strength": 1},
        "description": "A wielder of arcane power. High MP and Intelligence. Learns powerful spells.",
        "symbol": "✦",
    },
    "Ranger": {
        "strength": 4, "intelligence": 4, "agility": 8,
        "vitality": 4, "luck": 5, "perception": 7,
        "hp": 80, "mp": 60,
        "stat_growth": {"agility": 3, "perception": 2, "luck": 2, "strength": 1, "intelligence": 1, "vitality": 1},
        "description": "A swift hunter of beasts. High Agility and Perception. Learns tracking and trap skills.",
        "symbol": "🏹",
    },
}

def max_hp(vitality, base_hp, level):
    return base_hp + vitality * 8 + level * 5

def max_mp(intelligence, base_mp, level):
    return base_mp + intelligence * 6 + level * 3

def physical_damage(strength, weapon_dmg=0):
    return strength * 2 + weapon_dmg

def magic_damage(intelligence, spell_power=0):
    return intelligence * 2 + spell_power

def dodge_chance(agility):
    """Returns float 0.0–0.45"""
    return min(0.45, agility * 0.015)

def crit_chance(luck, agility):
    """Returns float 0.0–0.40"""
    return min(0.40, luck * 0.01 + agility * 0.005)

def crit_multiplier():
    return 1.75

def initiative(agility, perception):
    return agility + perception

def loot_bonus(luck):
    """Extra loot roll bonus 0.0–0.30"""
    return min(0.30, luck * 0.01)

def xp_for_level(level):
    return int(60 * (level ** 1.25))

def stat_points_per_level():
    return 3
