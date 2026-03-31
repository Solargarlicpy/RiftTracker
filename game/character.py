"""
Player character class.
"""
import copy
from .stats import (CLASS_BASES, max_hp, max_mp, physical_damage, magic_damage,
                    dodge_chance, crit_chance, crit_multiplier, initiative,
                    loot_bonus, xp_for_level, stat_points_per_level)
from .items import SLOTS


class Character:
    def __init__(self, name, cls_name):
        self.name = name
        self.cls_name = cls_name
        cfg = CLASS_BASES[cls_name]

        # Base stats
        self.strength     = cfg["strength"]
        self.intelligence = cfg["intelligence"]
        self.agility      = cfg["agility"]
        self.vitality     = cfg["vitality"]
        self.luck         = cfg["luck"]
        self.perception   = cfg["perception"]

        self._base_hp = cfg["hp"]
        self._base_mp = cfg["mp"]
        self._stat_growth = cfg["stat_growth"]

        # Leveling
        self.level   = 1
        self.xp      = 0
        self.xp_next = xp_for_level(2)
        self.stat_points = 0
        self.gold    = 20

        # Derived
        self.max_hp = max_hp(self.vitality, self._base_hp, self.level)
        self.max_mp = max_mp(self.intelligence, self._base_mp, self.level)
        self.hp     = self.max_hp
        self.mp     = self.max_mp

        # Skills & status
        self.skills  = []       # learned skill names
        self.skill_cooldowns = {}  # name -> remaining turns
        self.status_effects  = []  # "poisoned", "stunned", "slowed", ...
        self.temp_buffs      = {}  # name -> {stat, amount, turns_left}
        self.evasion_active  = False
        self.shadow_step_active = False

        # Equipment & inventory
        self.equipment = {slot: None for slot in SLOTS}
        self.inventory = []      # list of Item objects
        self.max_inv   = 20

    # ── Derived stat helpers ────────────────────────────────────────────────

    def get_stat(self, stat):
        base = getattr(self, stat, 0)
        bonus = sum(
            b["amount"] for b in self.temp_buffs.values()
            if b.get("stat") == stat
        )
        # Equipment bonuses
        for item in self.equipment.values():
            if item and hasattr(item, 'stat_bonus'):
                bonus += item.stat_bonus.get(stat, 0)
        return base + bonus

    def get_defense(self, dtype=None):
        armor_def = sum(
            item.defense for item in self.equipment.values()
            if item and hasattr(item, 'defense')
        )
        base = armor_def
        if dtype == "magic":
            base = int(armor_def * 0.5) + self.get_stat("intelligence") // 2
        elif dtype == "ranged":
            base = int(armor_def * 0.75) + self.get_stat("agility") // 3
        return base

    def get_attack_damage(self):
        weapon = self.equipment.get("weapon")
        wdmg = weapon.damage if weapon else 0
        dtype = weapon.damage_type if weapon else "physical"
        if dtype == "magic":
            return magic_damage(self.get_stat("intelligence"), wdmg)
        elif dtype == "ranged":
            return int(self.get_stat("agility") * 1.5 + wdmg)
        else:
            return physical_damage(self.get_stat("strength"), wdmg)

    def get_dodge(self):
        base = dodge_chance(self.get_stat("agility"))
        if self.evasion_active:
            base = min(0.80, base + 0.40)
        return base

    def get_crit(self):
        return crit_chance(self.get_stat("luck"), self.get_stat("agility"))

    def get_initiative(self):
        return initiative(self.get_stat("agility"), self.get_stat("perception"))

    def get_loot_bonus(self):
        return loot_bonus(self.get_stat("luck"))

    # ── Leveling ────────────────────────────────────────────────────────────

    def gain_xp(self, amount):
        self.xp += amount
        levels_gained = 0
        while self.xp >= self.xp_next:
            self.xp -= self.xp_next
            self.level_up()
            levels_gained += 1
        return levels_gained

    def level_up(self):
        self.level += 1
        self.xp_next = xp_for_level(self.level + 1)
        self.stat_points += stat_points_per_level()
        # Auto stat gains from growth template
        for stat, gain in self._stat_growth.items():
            if stat in ("hp", "mp"):
                continue
            current = getattr(self, stat)
            setattr(self, stat, current + (1 if gain >= 3 else 0))
        self._recalc_max()
        self.hp = self.max_hp
        self.mp = self.max_mp

    def _recalc_max(self):
        self.max_hp = max_hp(self.vitality, self._base_hp, self.level)
        self.max_mp = max_mp(self.intelligence, self._base_mp, self.level)

    def allocate_stat(self, stat):
        if self.stat_points > 0 and hasattr(self, stat):
            setattr(self, stat, getattr(self, stat) + 1)
            self.stat_points -= 1
            self._recalc_max()
            return True
        return False

    # ── Combat helpers ──────────────────────────────────────────────────────

    def tick_effects(self):
        """Called at the start of player's turn. Returns list of messages."""
        msgs = []
        # Poison
        if "poisoned" in self.status_effects:
            dmg = max(1, int(self.max_hp * 0.05))
            self.hp = max(0, self.hp - dmg)
            msgs.append(f"Poison deals {dmg} damage to {self.name}!")
        # Stun wears off
        if "stunned" in self.status_effects:
            self.status_effects.remove("stunned")
            msgs.append(f"{self.name} is no longer stunned.")
        # Slow
        if "slowed" in self.status_effects:
            self.status_effects.remove("slowed")

        # Temp buffs
        to_remove = []
        for bname, bdata in self.temp_buffs.items():
            bdata["turns_left"] -= 1
            if bdata["turns_left"] <= 0:
                to_remove.append(bname)
                msgs.append(f"{bname} effect has worn off.")
        for b in to_remove:
            del self.temp_buffs[b]

        # Evasion (1 turn)
        if self.evasion_active:
            self.evasion_active = False

        # Shadow step wears off after being used (handled in combat)
        return msgs

    def tick_cooldowns(self):
        for sk in list(self.skill_cooldowns):
            self.skill_cooldowns[sk] -= 1
            if self.skill_cooldowns[sk] <= 0:
                del self.skill_cooldowns[sk]

    def apply_effect(self, effect, value=1):
        if effect == "stun":
            if "stunned" not in self.status_effects:
                self.status_effects.append("stunned")
        elif effect == "poison":
            if "poisoned" not in self.status_effects:
                self.status_effects.append("poisoned")
        elif effect == "slow":
            if "slowed" not in self.status_effects:
                self.status_effects.append("slowed")
            # Reduce agility temporarily
            if "slow" not in self.temp_buffs:
                self.temp_buffs["slow"] = {"stat": "agility", "amount": -3, "turns_left": value}
        elif effect == "buff_str":
            self.temp_buffs["Battle Cry"] = {"stat": "strength", "amount": 5, "turns_left": value}
        elif effect == "evasion":
            self.evasion_active = True
        elif effect == "shadow_step":
            self.shadow_step_active = True

    def is_alive(self):
        return self.hp > 0

    # ── Inventory / Equipment ───────────────────────────────────────────────

    def pick_up(self, item):
        if len(self.inventory) >= self.max_inv:
            return False, "Inventory full!"
        self.inventory.append(item)
        return True, f"Picked up: {item}"

    def drop_item(self, index):
        if 0 <= index < len(self.inventory):
            item = self.inventory.pop(index)
            return item
        return None

    def equip(self, index):
        if not (0 <= index < len(self.inventory)):
            return False, "Invalid item."
        item = self.inventory[index]
        if item.itype not in ("weapon", "armor"):
            return False, f"{item.name} cannot be equipped."
        slot = item.slot
        old = self.equipment.get(slot)
        self.equipment[slot] = item
        self.inventory.pop(index)
        if old:
            self.inventory.append(old)
        self._recalc_max()
        msg = f"Equipped {item.name}."
        if old:
            msg += f" (Unequipped {old.name}.)"
        return True, msg

    def unequip(self, slot):
        item = self.equipment.get(slot)
        if not item:
            return False, "Nothing equipped there."
        if len(self.inventory) >= self.max_inv:
            return False, "Inventory full!"
        self.inventory.append(item)
        self.equipment[slot] = None
        self._recalc_max()
        return True, f"Unequipped {item.name}."

    def use_item(self, index):
        if not (0 <= index < len(self.inventory)):
            return False, "Invalid item."
        item = self.inventory[index]
        if item.itype == "consumable":
            msg = item.use(self)
            self.inventory.pop(index)
            return True, msg
        elif item.itype == "book":
            if item.skill_name in self.skills:
                return False, f"You already know {item.skill_name}."
            from .skills import SKILLS
            sk = SKILLS.get(item.skill_name)
            if sk and self.cls_name not in sk.get("classes", [self.cls_name]):
                return False, f"Only {'/'.join(sk['classes'])} can learn this skill."
            self.skills.append(item.skill_name)
            self.inventory.pop(index)
            return True, f"Learned skill: {item.skill_name}!"
        else:
            return False, "You can't use that directly. Try equipping it."

    # ── Display ─────────────────────────────────────────────────────────────

    def stat_block(self):
        lines = [
            f"  Name  : {self.name}  [{self.cls_name}]  Lv.{self.level}",
            f"  HP    : {self.hp}/{self.max_hp}",
            f"  MP    : {self.mp}/{self.max_mp}",
            f"  XP    : {self.xp}/{self.xp_next}",
            f"  Gold  : {self.gold}g",
            "",
            f"  STR {self.get_stat('strength'):>3}  INT {self.get_stat('intelligence'):>3}  "
            f"AGI {self.get_stat('agility'):>3}",
            f"  VIT {self.get_stat('vitality'):>3}  LCK {self.get_stat('luck'):>3}  "
            f"PER {self.get_stat('perception'):>3}",
        ]
        if self.stat_points:
            lines.append(f"  ** {self.stat_points} unspent stat point(s)! **")
        return lines
