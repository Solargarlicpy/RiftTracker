"""
Enemy definitions and scaling.
"""
import random
import copy


class Enemy:
    def __init__(self, name, hp, mp, strength, intelligence, agility,
                 vitality, defense, xp_reward, gold_min, gold_max,
                 attacks, description="", level=1, status_immune=None):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.mp = mp
        self.max_mp = mp
        self.strength = strength
        self.intelligence = intelligence
        self.agility = agility
        self.vitality = vitality
        self.defense = defense
        self.xp_reward = xp_reward
        self.gold_min = gold_min
        self.gold_max = gold_max
        self.attacks = attacks          # list of dicts: {name, damage, type, mp_cost, chance, effect}
        self.description = description
        self.level = level
        self.status_immune = status_immune or []
        self.status_effects = []
        self.temp_debuffs = {}

    def get_stat(self, stat):
        base = getattr(self, stat, 0)
        bonus = 0
        for bdata in self.temp_debuffs.values():
            if bdata.get("stat") == stat:
                bonus += bdata["amount"]
        return max(0, base + bonus)

    def get_defense(self, dtype=None):
        if dtype == "magic":
            return int(self.defense * 0.6)
        elif dtype == "ranged":
            return int(self.defense * 0.8)
        return self.defense

    def choose_attack(self):
        eligible = [a for a in self.attacks if self.mp >= a.get("mp_cost", 0)]
        if not eligible:
            eligible = [self.attacks[0]]
        weights = [a.get("chance", 1.0) for a in eligible]
        return random.choices(eligible, weights=weights, k=1)[0]

    def tick_effects(self):
        msgs = []
        if "poisoned" in self.status_effects:
            dmg = max(1, int(self.max_hp * 0.06))
            self.hp = max(0, self.hp - dmg)
            msgs.append(f"Poison eats at {self.name} for {dmg} damage!")
        if "stunned" in self.status_effects:
            self.status_effects.remove("stunned")
        if "slowed" in self.status_effects:
            self.status_effects.remove("slowed")
        to_remove = []
        for k, v in self.temp_debuffs.items():
            v["turns_left"] -= 1
            if v["turns_left"] <= 0:
                to_remove.append(k)
        for k in to_remove:
            del self.temp_debuffs[k]
        return msgs

    def apply_effect(self, effect, value=1):
        if effect in self.status_immune:
            return False
        if effect == "stun" and "stunned" not in self.status_effects:
            self.status_effects.append("stunned")
        elif effect == "poison" and "poisoned" not in self.status_effects:
            self.status_effects.append("poisoned")
        elif effect == "slow":
            if "slowed" not in self.status_effects:
                self.status_effects.append("slowed")
            self.temp_debuffs["slow"] = {"stat": "agility", "amount": -3, "turns_left": value}
        return True

    def is_alive(self):
        return self.hp > 0

    def gold_drop(self):
        return random.randint(self.gold_min, self.gold_max)

    def scale_to_level(self, player_level):
        """Return a level-scaled copy of this enemy."""
        e = copy.deepcopy(self)
        factor = 1 + (player_level - 1) * 0.12
        e.hp = e.max_hp = max(10, int(e.hp * factor))
        e.strength = int(e.strength * factor)
        e.intelligence = int(e.intelligence * factor)
        e.agility = int(e.agility * factor)
        e.defense = int(e.defense * factor)
        e.xp_reward = int(e.xp_reward * factor)
        e.gold_min = int(e.gold_min * factor)
        e.gold_max = int(e.gold_max * factor)
        e.level = player_level
        for atk in e.attacks:
            atk["damage"] = max(1, int(atk["damage"] * factor))
        return e


# ── Enemy Templates ──────────────────────────────────────────────────────────

ENEMY_POOL = [
    # ── Tier 1 ───────────────────────────────────────────────────────────────
    Enemy(
        name="Goblin Scout", hp=38, mp=0, strength=4, intelligence=1, agility=6,
        vitality=3, defense=2, xp_reward=25, gold_min=2, gold_max=8,
        description="A small, wiry creature with beady eyes and a rusty blade.",
        attacks=[
            {"name": "Stab",      "damage": 7,  "type": "physical", "chance": 0.7},
            {"name": "Sneak Jab", "damage": 12, "type": "physical", "chance": 0.3},
        ],
    ),
    Enemy(
        name="Giant Rat", hp=28, mp=0, strength=3, intelligence=0, agility=5,
        vitality=2, defense=1, xp_reward=15, gold_min=0, gold_max=3,
        description="An oversized rodent with matted fur and vicious teeth.",
        attacks=[
            {"name": "Bite",    "damage": 6,  "type": "physical", "chance": 0.6, "effect": "poison"},
            {"name": "Scratch", "damage": 5,  "type": "physical", "chance": 0.4},
        ],
    ),
    Enemy(
        name="Skeleton Archer", hp=44, mp=10, strength=3, intelligence=2, agility=5,
        vitality=2, defense=3, xp_reward=30, gold_min=3, gold_max=10,
        description="A rattling undead soldier that still holds a tarnished bow.",
        attacks=[
            {"name": "Arrow Shot", "damage": 10, "type": "ranged",   "chance": 0.6},
            {"name": "Bone Club",  "damage": 7,  "type": "physical", "chance": 0.4},
        ],
    ),
    Enemy(
        name="Slime", hp=50, mp=0, strength=2, intelligence=0, agility=1,
        vitality=8, defense=4, xp_reward=20, gold_min=0, gold_max=5,
        description="A quivering blob of acidic goo.",
        attacks=[
            {"name": "Acid Splash", "damage": 8,  "type": "magic",    "chance": 0.5, "effect": "poison"},
            {"name": "Slam",        "damage": 6,  "type": "physical", "chance": 0.5},
        ],
        status_immune=["poisoned"],
    ),

    # ── Tier 2 ───────────────────────────────────────────────────────────────
    Enemy(
        name="Orc Warrior", hp=70, mp=0, strength=9, intelligence=2, agility=4,
        vitality=8, defense=7, xp_reward=60, gold_min=8, gold_max=20,
        description="A muscular green-skinned brute with a chipped axe.",
        attacks=[
            {"name": "Axe Swing",   "damage": 14, "type": "physical", "chance": 0.5},
            {"name": "Cleave",      "damage": 18, "type": "physical", "chance": 0.3},
            {"name": "War Shout",   "damage": 8,  "type": "physical", "chance": 0.2},
        ],
    ),
    Enemy(
        name="Dark Mage", hp=45, mp=60, strength=2, intelligence=9, agility=4,
        vitality=4, defense=3, xp_reward=65, gold_min=10, gold_max=25,
        description="A robed figure wreathed in crackling dark energy.",
        attacks=[
            {"name": "Shadow Bolt", "damage": 16, "type": "magic",    "chance": 0.5, "mp_cost": 8},
            {"name": "Curse",       "damage": 10, "type": "magic",    "chance": 0.3, "mp_cost": 5, "effect": "poison"},
            {"name": "Staff Hit",   "damage": 6,  "type": "physical", "chance": 0.2},
        ],
    ),
    Enemy(
        name="Forest Bandit", hp=55, mp=0, strength=7, intelligence=3, agility=8,
        vitality=5, defense=5, xp_reward=52, gold_min=12, gold_max=30,
        description="A nimble highwayman with twin daggers.",
        attacks=[
            {"name": "Dual Slash",  "damage": 12, "type": "physical", "chance": 0.5},
            {"name": "Poison Jab",  "damage": 8,  "type": "physical", "chance": 0.3, "effect": "poison"},
            {"name": "Cheap Shot",  "damage": 15, "type": "physical", "chance": 0.2},
        ],
    ),
    Enemy(
        name="Stone Golem", hp=110, mp=0, strength=12, intelligence=0, agility=1,
        vitality=14, defense=15, xp_reward=95, gold_min=5, gold_max=15,
        description="A slow but nearly indestructible animated statue.",
        attacks=[
            {"name": "Fist Smash",   "damage": 20, "type": "physical", "chance": 0.6},
            {"name": "Ground Slam",  "damage": 28, "type": "physical", "chance": 0.4},
        ],
        status_immune=["poisoned", "stunned"],
    ),

    # ── Tier 3 ───────────────────────────────────────────────────────────────
    Enemy(
        name="Vampire Lord", hp=130, mp=80, strength=12, intelligence=10, agility=10,
        vitality=10, defense=10, xp_reward=165, gold_min=30, gold_max=60,
        description="An ancient undead noble who feeds on the living.",
        attacks=[
            {"name": "Blood Drain",   "damage": 20, "type": "magic",    "chance": 0.4, "mp_cost": 10},
            {"name": "Bat Swarm",     "damage": 14, "type": "physical", "chance": 0.3},
            {"name": "Hypnotic Gaze", "damage": 12, "type": "magic",    "chance": 0.3, "mp_cost": 8, "effect": "stun"},
        ],
        status_immune=["poisoned"],
    ),
    Enemy(
        name="Wyvern", hp=160, mp=30, strength=15, intelligence=5, agility=12,
        vitality=12, defense=12, xp_reward=190, gold_min=25, gold_max=55,
        description="A fearsome two-legged dragon with a barbed tail.",
        attacks=[
            {"name": "Claw Slash",  "damage": 22, "type": "physical", "chance": 0.4},
            {"name": "Tail Whip",   "damage": 18, "type": "physical", "chance": 0.3},
            {"name": "Fire Breath", "damage": 30, "type": "magic",    "chance": 0.3, "mp_cost": 10},
        ],
    ),
    Enemy(
        name="Rift Wraith", hp=100, mp=120, strength=5, intelligence=15, agility=14,
        vitality=6, defense=5, xp_reward=175, gold_min=20, gold_max=50,
        description="A spectral horror born from a dimensional rift.",
        attacks=[
            {"name": "Soul Rend",   "damage": 25, "type": "magic",    "chance": 0.4, "mp_cost": 15},
            {"name": "Phase Strike","damage": 18, "type": "magic",    "chance": 0.4, "mp_cost": 10},
            {"name": "Wail",        "damage": 12, "type": "magic",    "chance": 0.2, "mp_cost": 5, "effect": "stun"},
        ],
        status_immune=["poisoned", "slowed"],
    ),

]

ENEMY_BY_NAME = {e.name: e for e in ENEMY_POOL}


def get_enemy_for_level(player_level):
    if player_level <= 4:
        pool = ENEMY_POOL[0:4]
    elif player_level <= 9:
        pool = ENEMY_POOL[0:8]
    elif player_level <= 14:
        pool = ENEMY_POOL[4:11]
    else:
        pool = ENEMY_POOL[7:11]
    template = random.choice(pool)
    return template.scale_to_level(player_level)


# ── Boss Pool ─────────────────────────────────────────────────────────────────

BOSS_POOL = [
    {
        "min_level": 5,
        "announcement": "The vault floor shudders. From the dark steps the IRON BULWARK.",
        "enemy": Enemy(
            name="Iron Bulwark", hp=220, mp=20, strength=14, intelligence=2, agility=3,
            vitality=18, defense=20, xp_reward=200, gold_min=40, gold_max=80,
            description="A colossal animated suit of armour, ancient guardian of a forgotten vault. Its joints grind with each thunderous step.",
            attacks=[
                {"name": "Iron Fist",     "damage": 22, "type": "physical", "chance": 0.45},
                {"name": "Crushing Blow", "damage": 34, "type": "physical", "chance": 0.30},
                {"name": "Slam Down",     "damage": 18, "type": "physical", "chance": 0.25, "effect": "stun"},
            ],
            status_immune=["stunned", "poisoned"],
        ),
    },
    {
        "min_level": 8,
        "announcement": "The ceiling cracks. Eight legs lower a creature the size of a cart — THE VENOM MATRIARCH.",
        "enemy": Enemy(
            name="The Venom Matriarch", hp=300, mp=60, strength=10, intelligence=8, agility=14,
            vitality=10, defense=10, xp_reward=280, gold_min=55, gold_max=105,
            description="An ancient spider of monstrous size. Her venom can dissolve stone. Ten thousand young await her signal.",
            attacks=[
                {"name": "Fang Strike",  "damage": 18, "type": "physical", "chance": 0.40, "effect": "poison"},
                {"name": "Web Snare",    "damage": 10, "type": "physical", "chance": 0.30, "effect": "slow"},
                {"name": "Venom Spray",  "damage": 24, "type": "magic",    "chance": 0.30, "mp_cost": 15, "effect": "poison"},
            ],
            status_immune=["poisoned"],
        ),
    },
    {
        "min_level": 11,
        "announcement": "The air reeks of ash and old rage. ASHREN THE UNBURNT rises from the embers.",
        "enemy": Enemy(
            name="Ashren the Unburnt", hp=370, mp=100, strength=16, intelligence=14, agility=8,
            vitality=15, defense=14, xp_reward=360, gold_min=70, gold_max=130,
            description="A fire knight who died mid-charge and never stopped burning. His hatred outlasted his flesh.",
            attacks=[
                {"name": "Flame Slash",    "damage": 28, "type": "physical", "chance": 0.35},
                {"name": "Ash Cloud",      "damage": 24, "type": "magic",    "chance": 0.35, "mp_cost": 12, "effect": "stun"},
                {"name": "Inferno Charge", "damage": 40, "type": "physical", "chance": 0.30, "mp_cost": 20},
            ],
            status_immune=["poisoned", "slowed"],
        ),
    },
    {
        "min_level": 15,
        "announcement": "Reality tears open. From the wound steps THE RIFT SOVEREIGN — ruler of the void between worlds.",
        "enemy": Enemy(
            name="The Rift Sovereign", hp=450, mp=200, strength=20, intelligence=20, agility=16,
            vitality=20, defense=18, xp_reward=650, gold_min=100, gold_max=200,
            description="The ancient ruler of the rift dimension. Its mere presence warps reality.",
            attacks=[
                {"name": "Void Slash",    "damage": 35, "type": "physical", "chance": 0.25},
                {"name": "Rift Blast",    "damage": 45, "type": "magic",    "chance": 0.25, "mp_cost": 20},
                {"name": "Reality Tear",  "damage": 55, "type": "magic",    "chance": 0.20, "mp_cost": 30},
                {"name": "Temporal Crush","damage": 40, "type": "physical", "chance": 0.15},
                {"name": "Annihilate",    "damage": 70, "type": "magic",    "chance": 0.15, "mp_cost": 40},
            ],
            status_immune=["poisoned", "stunned", "slowed"],
        ),
    },
]


def get_available_boss(player_level, killed_bosses):
    """Return a random eligible boss, or None. Prioritises unkilled bosses."""
    unkilled = [b for b in BOSS_POOL
                if player_level >= b["min_level"] and b["enemy"].name not in killed_bosses]
    if unkilled:
        return random.choice(unkilled)
    # All eligible bosses already killed — allow re-fights at reduced chance
    killed_eligible = [b for b in BOSS_POOL if player_level >= b["min_level"]]
    return random.choice(killed_eligible) if killed_eligible else None
