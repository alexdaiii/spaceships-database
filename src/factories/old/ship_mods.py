import json
import os

import numpy as np
from pydantic import BaseModel, Field

from src.models import SpaceshipModule
from src.util import get_location

NUM_TECH_LEVELS = 6


class GeneralMods(BaseModel):
    power: list[str] = Field(
        max_items=NUM_TECH_LEVELS, min_items=NUM_TECH_LEVELS
    )
    ftl: list[str] = Field(
        max_items=NUM_TECH_LEVELS, min_items=NUM_TECH_LEVELS
    )
    thrusters: list[str] = Field(
        max_items=NUM_TECH_LEVELS, min_items=NUM_TECH_LEVELS
    )
    computer: list[str] = Field(
        max_items=NUM_TECH_LEVELS, min_items=NUM_TECH_LEVELS
    )


class WeaponClass(BaseModel):
    value: list[str]
    base_power: int


class WeaponMods(BaseModel):
    small: WeaponClass
    medium: WeaponClass
    large: WeaponClass
    xlarge: WeaponClass
    giga: WeaponClass
    titan: WeaponClass
    juggernaut: WeaponClass
    colossus: WeaponClass
    star_eater: WeaponClass


class DefenseMods(BaseModel):
    armor: list[str] = Field(
        max_items=NUM_TECH_LEVELS, min_items=NUM_TECH_LEVELS
    )
    shield: list[str] = Field(
        max_items=NUM_TECH_LEVELS, min_items=NUM_TECH_LEVELS
    )
    auxiliary: list[str]


class CombatMods(BaseModel):
    sensors: list[str] = Field(
        max_items=NUM_TECH_LEVELS, min_items=NUM_TECH_LEVELS
    )
    weapons: WeaponMods
    defense: DefenseMods


class ModType(BaseModel):
    general: GeneralMods
    combat: CombatMods


def unpack_mods_base(
    mod_list: list[str],
    *,
    rng: np.random.Generator,
    mods: list[SpaceshipModule],
    mod_name_to_id: dict[str, int],
    is_combat: bool,
    is_tech: bool,
):
    """
    Base case for unpacking the list and creating the SpaceshipModules.
    """
    power_mult = 1 if is_combat else 0.1

    if is_tech:
        # should have increasing power and weights

        power_levels = np.linspace(0, 1, num=len(mod_list))
        weights = np.linspace(0, 1, num=len(mod_list))
    else:
        # should have random power and weights near each other

        power_levels = rng.normal(size=len(mod_list))

    for i, mod_name in enumerate(mod_list, start=len(mods) + 1):
        mods.append(
            SpaceshipModule(
                spaceship_module_id=i,
                spaceship_module_name=mod_name,
                spaceship_module_weight=rng.integers(),
            )
        )
        mod_name_to_id[mod_name] = i


tech_level_keys = {
    "power",
    "ftl",
    "thrusters",
    "computer",
    "armor",
    "shield",
    "sensors",
}


def unpack_mods(
    mod_dict: dict | list,
    *,
    rng: np.random.Generator,
    dict_key: str,
    is_combat: bool,
    mods: list[SpaceshipModule],
    mod_name_to_id: dict[str, int],
):
    """
    Recursively unpack the mods from the mod dictionary.
    """

    # base case
    if not isinstance(mod_dict, dict):
        if not isinstance(mod_dict, list):
            raise TypeError("mod_dict must be a dict or list")

        unpack_mods_base(
            mod_dict,
            rng=rng,
            mods=mods,
            mod_name_to_id=mod_name_to_id,
            is_combat=is_combat,
            is_tech=dict_key in tech_level_keys,
        )
        return


def create_ship_module():
    ship_mod_file = "../assets/ship_mods.json"

    with open(os.path.join(get_location(), ship_mod_file)) as f:
        ship_mods = ModType(**json.load(f))

    mods = []
    mod_name_to_id = {}

    # pretty print
    print(ship_mods.model_dump_json(indent=2))
