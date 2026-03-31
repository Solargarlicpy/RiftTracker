"""
Item definitions: weapons, armor, consumables, books, misc loot.
"""
import random

RARITIES = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
RARITY_COLOR = {"Common": "dim", "Uncommon": "green", "Rare": "blue",
                "Epic": "magenta", "Legendary": "yellow"}
RARITY_WEIGHT = [55, 25, 12, 6, 2]

SLOTS = ["head", "chest", "legs", "feet", "hands", "weapon", "offhand", "ring", "amulet"]


class Item:
    def __init__(self, name, itype, description="", value=1, weight=1.0, rarity="Common"):
        self.name = name
        self.itype = itype          # weapon / armor / consumable / book / misc
        self.description = description
        self.value = value
        self.weight = weight
        self.rarity = rarity

    def __str__(self):
        return f"{self.name} [{self.rarity}]"

    def to_dict(self):
        return self.__dict__.copy()


class Weapon(Item):
    def __init__(self, name, damage, damage_type, slot="weapon",
                 stat_bonus=None, description="", value=10, weight=2.0,
                 rarity="Common", two_handed=False, skill_req=None):
        super().__init__(name, "weapon", description, value, weight, rarity)
        self.damage = damage
        self.damage_type = damage_type  # physical / magic / ranged
        self.slot = slot
        self.stat_bonus = stat_bonus or {}
        self.two_handed = two_handed
        self.skill_req = skill_req


class Armor(Item):
    def __init__(self, name, slot, defense, stat_bonus=None,
                 description="", value=10, weight=3.0, rarity="Common"):
        super().__init__(name, "armor", description, value, weight, rarity)
        self.slot = slot
        self.defense = defense
        self.stat_bonus = stat_bonus or {}


class Consumable(Item):
    def __init__(self, name, effect, amount, description="", value=5, weight=0.5, rarity="Common"):
        super().__init__(name, "consumable", description, value, weight, rarity)
        self.effect = effect    # "heal_hp", "heal_mp", "buff_str", etc.
        self.amount = amount

    def use(self, player):
        msg = ""
        if self.effect == "heal_hp":
            healed = min(self.amount, player.max_hp - player.hp)
            player.hp += healed
            msg = f"Restored {healed} HP."
        elif self.effect == "heal_mp":
            restored = min(self.amount, player.max_mp - player.mp)
            player.mp += restored
            msg = f"Restored {restored} MP."
        elif self.effect == "full_heal":
            player.hp = player.max_hp
            msg = "HP fully restored!"
        elif self.effect == "antidote":
            if "poisoned" in player.status_effects:
                player.status_effects.remove("poisoned")
                msg = "Poison cured!"
            else:
                msg = "You aren't poisoned."
        elif self.effect == "revive":
            player.hp = max(1, player.max_hp // 2)
            msg = "Revived with half HP!"
        return msg


class SkillBook(Item):
    def __init__(self, name, skill_name, description="", value=50, rarity="Uncommon"):
        super().__init__(name, "book", description, value, 0.5, rarity)
        self.skill_name = skill_name


# ── Pre-built item tables ────────────────────────────────────────────────────

WEAPONS = [
    Weapon("Rusty Sword",       damage=8,  damage_type="physical", rarity="Common",   value=5),
    Weapon("Iron Sword",        damage=14, damage_type="physical", rarity="Common",   value=20),
    Weapon("Steel Longsword",   damage=22, damage_type="physical", rarity="Uncommon", value=60, two_handed=True),
    Weapon("Flamebrand",        damage=28, damage_type="physical", rarity="Rare",     value=150, stat_bonus={"intelligence": 2}),
    Weapon("Obsidian Greatsword", damage=40, damage_type="physical", rarity="Epic",   value=400, two_handed=True, stat_bonus={"strength": 4}),
    Weapon("Wraith's Edge",     damage=55, damage_type="physical", rarity="Legendary", value=900, stat_bonus={"agility": 5, "strength": 5}),

    Weapon("Gnarled Staff",     damage=6,  damage_type="magic",    rarity="Common",   value=8),
    Weapon("Mage's Rod",        damage=12, damage_type="magic",    rarity="Common",   value=22),
    Weapon("Arcane Staff",      damage=20, damage_type="magic",    rarity="Uncommon", value=75, stat_bonus={"intelligence": 3}),
    Weapon("Void Scepter",      damage=32, damage_type="magic",    rarity="Rare",     value=180, stat_bonus={"intelligence": 5}),
    Weapon("Staff of Eternity", damage=50, damage_type="magic",    rarity="Legendary", value=1000, stat_bonus={"intelligence": 8, "perception": 4}),

    Weapon("Shortbow",          damage=10, damage_type="ranged",   rarity="Common",   value=12),
    Weapon("Longbow",           damage=18, damage_type="ranged",   rarity="Common",   value=35, two_handed=True),
    Weapon("Hunter's Bow",      damage=26, damage_type="ranged",   rarity="Uncommon", value=80, stat_bonus={"agility": 2}),
    Weapon("Elven Recurve",     damage=36, damage_type="ranged",   rarity="Rare",     value=200, stat_bonus={"agility": 4, "perception": 3}),
    Weapon("Riftbow",           damage=52, damage_type="ranged",   rarity="Legendary", value=950, stat_bonus={"agility": 6, "luck": 4}),

    Weapon("Rusty Dagger",      damage=5,  damage_type="physical", rarity="Common",   value=4),
    Weapon("Poison Dagger",     damage=9,  damage_type="physical", rarity="Uncommon", value=55, stat_bonus={"luck": 2}),
]

# ── Starting weapons (character creation only, not in loot pool) ─────────────
STARTING_WEAPONS = [
    Weapon(
        "Worn Shortsword", damage=7, damage_type="physical", rarity="Common", value=0,
        stat_bonus={"strength": 1},
        description="A nicked but balanced blade. Reliable in close quarters. +1 Strength.",
    ),
    Weapon(
        "Heavy Club", damage=10, damage_type="physical", rarity="Common", value=0,
        stat_bonus={},
        description="A dense hunk of ironwood. Hits hard but offers nothing else.",
    ),
    Weapon(
        "Cracked Staff", damage=6, damage_type="magic", rarity="Common", value=0,
        stat_bonus={"intelligence": 1},
        description="A staff etched with faded runes. Still channels arcane energy. +1 Intelligence.",
    ),
    Weapon(
        "Apprentice Wand", damage=5, damage_type="magic", rarity="Common", value=0,
        stat_bonus={"perception": 1},
        description="A slender wand tuned for precision casting. +1 Perception.",
    ),
    Weapon(
        "Hunting Bow", damage=6, damage_type="ranged", rarity="Common", value=0,
        stat_bonus={"agility": 1},
        description="A simple recurve bow carved from ash wood. +1 Agility.",
    ),
    Weapon(
        "Scout's Dagger", damage=5, damage_type="physical", rarity="Common", value=0,
        stat_bonus={"agility": 1, "luck": 1},
        description="A thin blade favored by thieves and scouts. +1 Agility, +1 Luck.",
    ),
]

ARMORS = [
    Armor("Leather Cap",       slot="head",    defense=3,  rarity="Common",   value=8),
    Armor("Iron Helm",         slot="head",    defense=7,  rarity="Common",   value=25),
    Armor("Knight's Helm",     slot="head",    defense=14, rarity="Uncommon", value=70, stat_bonus={"vitality": 1}),
    Armor("Mage's Hood",       slot="head",    defense=4,  rarity="Common",   value=15, stat_bonus={"intelligence": 2}),
    Armor("Shadow Cowl",       slot="head",    defense=6,  rarity="Rare",     value=120, stat_bonus={"agility": 2, "luck": 2}),

    Armor("Cloth Robe",        slot="chest",   defense=2,  rarity="Common",   value=6, stat_bonus={"intelligence": 1}),
    Armor("Leather Vest",      slot="chest",   defense=5,  rarity="Common",   value=12),
    Armor("Chainmail",         slot="chest",   defense=12, rarity="Common",   value=40),
    Armor("Plate Breastplate", slot="chest",   defense=20, rarity="Uncommon", value=110, stat_bonus={"strength": 1}),
    Armor("Arcane Vestments",  slot="chest",   defense=8,  rarity="Rare",     value=160, stat_bonus={"intelligence": 4, "vitality": 2}),
    Armor("Shadow Leathers",   slot="chest",   defense=10, rarity="Rare",     value=140, stat_bonus={"agility": 3}),
    Armor("Rift-Forged Plate", slot="chest",   defense=30, rarity="Epic",     value=500, stat_bonus={"vitality": 5, "strength": 3}),

    Armor("Wool Trousers",     slot="legs",    defense=2,  rarity="Common",   value=5),
    Armor("Leather Leggings",  slot="legs",    defense=5,  rarity="Common",   value=14),
    Armor("Iron Greaves",      slot="legs",    defense=10, rarity="Common",   value=35),
    Armor("Enchanted Slacks",  slot="legs",    defense=7,  rarity="Uncommon", value=60, stat_bonus={"agility": 2}),

    Armor("Worn Boots",        slot="feet",    defense=1,  rarity="Common",   value=3),
    Armor("Leather Boots",     slot="feet",    defense=4,  rarity="Common",   value=10),
    Armor("Swift Boots",       slot="feet",    defense=5,  rarity="Uncommon", value=50, stat_bonus={"agility": 3}),
    Armor("Iron Sabatons",     slot="feet",    defense=8,  rarity="Common",   value=30),

    Armor("Cloth Gloves",      slot="hands",   defense=1,  rarity="Common",   value=4),
    Armor("Leather Gloves",    slot="hands",   defense=3,  rarity="Common",   value=9),
    Armor("Iron Gauntlets",    slot="hands",   defense=7,  rarity="Common",   value=28),
    Armor("Spellweave Gloves", slot="hands",   defense=4,  rarity="Rare",     value=130, stat_bonus={"intelligence": 3}),

    Armor("Copper Ring",       slot="ring",    defense=0,  rarity="Common",   value=10, stat_bonus={"luck": 1}),
    Armor("Ring of Strength",  slot="ring",    defense=0,  rarity="Uncommon", value=60, stat_bonus={"strength": 3}),
    Armor("Ring of Sorcery",   slot="ring",    defense=0,  rarity="Rare",     value=150, stat_bonus={"intelligence": 4}),
    Armor("Lucky Charm Ring",  slot="ring",    defense=0,  rarity="Epic",     value=300, stat_bonus={"luck": 6}),

    Armor("Bone Amulet",       slot="amulet",  defense=0,  rarity="Common",   value=12),
    Armor("Vitality Pendant",  slot="amulet",  defense=0,  rarity="Uncommon", value=70, stat_bonus={"vitality": 4}),
    Armor("Rift Talisman",     slot="amulet",  defense=0,  rarity="Epic",     value=350, stat_bonus={"perception": 5, "luck": 3}),
]

CONSUMABLES = [
    Consumable("Health Potion",       "heal_hp",   40,  value=15, description="Restores 40 HP."),
    Consumable("Greater Health Potion",  "heal_hp",   80,  value=30, rarity="Uncommon", description="Restores 80 HP."),
    Consumable("Elixir of Life",      "full_heal", 0,   value=80, rarity="Rare", description="Fully restores HP."),
    Consumable("Mana Potion",         "heal_mp",   40,  value=15, description="Restores 40 MP."),
    Consumable("Greater Mana Potion",    "heal_mp",   80,  value=30, rarity="Uncommon", description="Restores 80 MP."),
    Consumable("Antidote",            "antidote",  0,   value=10, description="Cures poison."),
    Consumable("Phoenix Feather",     "revive",    0,   value=100, rarity="Rare", description="Revives with 50% HP."),
]

SKILL_BOOKS = [
    SkillBook("Tome of Power Strike",   "Power Strike",   value=80,  description="Learn Power Strike: heavy melee blow."),
    SkillBook("Scroll of Fireball",     "Fireball",       value=80,  description="Learn Fireball: explosive magic attack."),
    SkillBook("Manual of Steady Shot",  "Steady Shot",    value=80,  description="Learn Steady Shot: precise ranged attack."),
    SkillBook("Tome of Whirlwind",      "Whirlwind",      value=120, rarity="Rare", description="Learn Whirlwind: strike all enemies."),
    SkillBook("Scroll of Ice Shard",    "Ice Shard",      value=80,  description="Learn Ice Shard: slows enemy."),
    SkillBook("Tome of Bulwark Strike",  "Bulwark Strike",  value=80,  description="Learn Bulwark Strike: stuns enemy briefly."),
    SkillBook("Scroll of Arcane Blast", "Arcane Blast",   value=100, rarity="Uncommon", description="Learn Arcane Blast: pure magic damage."),
    SkillBook("Manual of Evasion",      "Evasion",        value=90,  rarity="Uncommon", description="Learn Evasion: greatly boosts dodge for one turn."),
    SkillBook("Tome of Battle Cry",     "Battle Cry",     value=90,  rarity="Uncommon", description="Learn Battle Cry: boost STR for 3 turns."),
    SkillBook("Scroll of Poison Arrow", "Poison Arrow",   value=75,  description="Learn Poison Arrow: poisons enemy."),
    SkillBook("Manual of Shade Step",  "Shade Step",  value=110, rarity="Rare", description="Learn Shade Step: skip enemy's next attack."),
    SkillBook("Tome of Shock Slam",   "Shock Slam",  value=130, rarity="Rare", description="Learn Shock Slam: AOE stun."),
    SkillBook("Scroll of Mana Drain",   "Mana Drain",     value=100, rarity="Uncommon", description="Learn Mana Drain: steal enemy HP as MP."),
    SkillBook("Ancient Codex",          "Rift Pulse",     value=300, rarity="Legendary", description="Learn Rift Pulse: devastating arcane explosion."),
]

GOLD_DROPS = [5, 10, 15, 20, 30, 40, 50, 75, 100, 150]


def random_rarity():
    return random.choices(RARITIES, weights=RARITY_WEIGHT, k=1)[0]


def random_item(level=1, luck_bonus=0.0):
    pool = WEAPONS + ARMORS + CONSUMABLES + SKILL_BOOKS

    # Higher rarities unlock progressively with level
    rare_scale   = min(1.0, max(0.0, (level - 2) / 7))   # unlocks from lv3
    epic_scale   = min(1.0, max(0.0, (level - 6) / 7))   # unlocks from lv7
    legend_scale = min(1.0, max(0.0, (level - 12) / 5))  # unlocks from lv13

    rarity_w = {
        "Common":    max(10, 55 - level),
        "Uncommon":  25,
        "Rare":      12 * rare_scale + luck_bonus * 8,
        "Epic":       6 * epic_scale + luck_bonus * 4,
        "Legendary":  2 * legend_scale + luck_bonus * 2,
    }

    weights = [max(0.01, rarity_w[item.rarity]) for item in pool]
    return random.choices(pool, weights=weights, k=1)[0]


def loot_table(level=1, luck_bonus=0.0, count=None):
    if count is None:
        # First item isn't guaranteed — chance grows with level
        drop_chance  = min(0.75, 0.35 + level * 0.04)
        extra_chance = min(0.30, luck_bonus * 0.5 + level * 0.015)

        count = 0
        if random.random() < drop_chance:
            count = 1
            if random.random() < extra_chance:
                count = 2
    return [random_item(level, luck_bonus) for _ in range(count)]
