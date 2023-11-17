import json
import math
import os

import numpy as np
from faker import Faker

from src.database.base import Base
from src.factories.utils import STARTING_ID, load_file, get_location
from src.models import ShipClass, Spaceship, SpaceshipModule

from pydantic import BaseModel, Field

_combat_ship_class = [
    "Corvette",
    "Frigate",
    "Destroyer",
    "Cruiser",
    "Battleship",
    "Titan",
    "Juggernaut",
    "Colossus",
    "StarEater",
]

_stationary_ship_class = [
    "Outpost",
    "Mining Station",
    "Research Station",
    "Observatory",
    "Shipyard",
    "Starbase",
]

_civilian_ship_class = [
    "Science Ship",
    "Colony Ship",
    "Construction Ship",
    "Transport Ship",
]


class ShipClassList:
    def __init__(self, value: list[str], weight: int):
        self.value = value
        self.weight = weight


def _create_ship_class():
    classes = []

    def append_to_classes(class_list: list[str], add_bonus: bool = False):
        start = len(classes) + 1
        ship_bonus_mult = 0.25
        return [
            ShipClass(
                ship_class_id=i,
                ship_class_name=class_name,
                ship_class_bonus=ship_bonus_mult * (i - start)
                if add_bonus
                else None,
            )
            for i, class_name in enumerate(class_list, start=start)
        ]

    classes.extend(append_to_classes(_combat_ship_class, add_bonus=True))
    classes.extend(append_to_classes(_stationary_ship_class))
    classes.extend(append_to_classes(_civilian_ship_class))

    return classes, {
        ship_class.ship_class_name: ship_class.ship_class_id
        for ship_class in classes
    }


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


class WeaponMods(BaseModel):
    small: list[str]
    medium: list[str]
    large: list[str]
    xlarge: list[str]
    giga: list[str]
    titan: list[str]
    juggernaut: list[str]
    colossus: list[str]
    star_eater: list[str]


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


def _create_ship_module():
    ship_mod_file = "ship_mods.json"

    with open(os.path.join(get_location(), ship_mod_file)) as f:
        ship_mods = ModType(**json.load(f))

    mods = []
    mod_name_to_id = {}

    def unpack_mods(mod_dict: dict | list, start_key: str, is_combat: bool):
        """
        Recursively unpack the mods from the mod dictionary.
        """

        # base case
        if not isinstance(mod_dict, dict):
            if not isinstance(mod_dict, list):
                raise TypeError("mod_dict must be a dict or list")

            for i, mod_name in enumerate(mod_dict, start=len(mods) + 1):
                mods.append(
                    SpaceshipModule(
                        spaceship_module_id=i,
                        spaceship_module_name=mod_name,
                    )
                )
                mod_name_to_id[mod_name] = i

    # pretty print
    print(ship_mods.model_dump_json(indent=2))


def _get_ship_class_id(
    fake: Faker, *, rng: np.random.Generator, ship_class_map: dict[str, int]
):
    """
    Gets the ship class ID for a ship and the experience level of the ship.
    Only combat ships have experience levels.

    Args:
        rng: numpy random generator
        fake: Faker instance
        ship_class_map: Mapping of ship class name to ship class ID

    Returns:
        Tuple of ship class ID and experience level
    """
    fleet_weights = {
        "combat": ShipClassList(_combat_ship_class, weight=100),
        "stationary": ShipClassList(_stationary_ship_class, weight=15),
        "civilian": ShipClassList(_civilian_ship_class, weight=5),
    }
    tot_fleet_weight: int = sum(val.weight for val in fleet_weights.values())
    combat_weight_base = 2.75
    combat_weights = {
        ship_class: combat_weight_base**i
        for i, ship_class in enumerate(reversed(_combat_ship_class))
    }
    tot_combat_weight = sum(combat_weights.values())
    mean_xp = 25

    ship_class: str = rng.choice(
        list(fleet_weights.keys()),
        p=[val.weight / tot_fleet_weight for val in fleet_weights.values()],
    )

    if ship_class == "combat":
        ship_class_name = rng.choice(
            _combat_ship_class,
            p=[
                combat_weights[ship] / tot_combat_weight
                for ship in _combat_ship_class
            ],
        )
        xp = max(rng.normal(mean_xp, mean_xp**1.5), 0)
    else:
        ship_class_name = fake.random_element(fleet_weights[ship_class].value)
        xp = None

    return ship_class_map[ship_class_name], xp


def _ships_for_fleet(
    fake: Faker,
    *,
    rng: np.random.Generator,
    start_id: int,
    fleet_id: int,
    ship_class_map: dict[str, int],
    max_ships: int,
):
    num_ships = math.ceil(rng.normal(loc=max_ships / 2, scale=max_ships / 10))
    ship_suffix = "ship_suffix.txt"
    prefix_num_letters = 3

    for ship_id, suffix in enumerate(
        fake.random_elements(
            elements=load_file(
                location=get_location(),
                filename=ship_suffix,
            ),
            length=num_ships,
            unique=True,
        ),
        start=start_id,
    ):
        ship_class_id, xp = _get_ship_class_id(
            fake=fake,
            ship_class_map=ship_class_map,
            rng=rng,
        )
        yield Spaceship(
            spaceship_id=ship_id,
            spaceship_name=f"{''.join([fake.random_uppercase_letter() for _ in range(prefix_num_letters)])} {suffix}",
            spaceship_fleet_id=fleet_id,
            spaceship_class_id=ship_class_id,
            spaceship_experience=xp,
        )


def create_ships(
    fake: Faker, *, rng: np.random.Generator, num_fleets: int, max_ships: int
):
    val: tuple[list[Base], dict] = _create_ship_class()
    inserts, ship_class_map = val

    _create_ship_module()

    for fleet_id in range(STARTING_ID, num_fleets + 1):
        inserts.extend(
            _ships_for_fleet(
                fake,
                rng=rng,
                start_id=len(inserts) + 1,
                fleet_id=fleet_id,
                ship_class_map=ship_class_map,
                max_ships=max_ships,
            )
        )

    return inserts


__all__ = ["create_ships"]

if __name__ == "__main__":
    fake = Faker()
    rng = np.random.default_rng(0)
    print(
        create_ships(
            fake=fake,
            rng=rng,
            num_fleets=1,
            max_ships=1,
        )
    )
