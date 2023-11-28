import json
import os
from functools import lru_cache

import pandas as pd
from pydantic import BaseModel, Field, computed_field

from src.util import get_location

weapon_field = Field(0, ge=0)
mods_tech_levels = Field(min_items=6, max_items=6)


class ShipWeaponInfo(BaseModel):
    small: int = weapon_field
    medium: int = weapon_field
    large: int = weapon_field
    xlarge: int = weapon_field
    titan: int = weapon_field
    juggernaut: int = weapon_field
    colossus: int = weapon_field
    star_eater: int = weapon_field


class ShipClassInfo(BaseModel):
    name: str
    weapons: ShipWeaponInfo
    command_points: int


class ShipWeaponModInfo(BaseModel):
    value: list[str]
    base_power: int


class ShipWeaponMod(BaseModel):
    small: ShipWeaponModInfo
    medium: ShipWeaponModInfo
    large: ShipWeaponModInfo
    xlarge: ShipWeaponModInfo
    titan: ShipWeaponModInfo
    juggernaut: ShipWeaponModInfo
    colossus: ShipWeaponModInfo
    star_eater: ShipWeaponModInfo


class ShipsInfo(BaseModel):
    ship_class: list[ShipClassInfo]
    ship_weapons: ShipWeaponMod

    @computed_field
    @property
    def ship_class_df(self) -> pd.DataFrame:
        print("Creating ship class df")
        return pd.DataFrame(
            [
                {
                    "ship_class_id": i,
                    "ship_class_name": ship_class.name,
                    **ship_class.weapons.model_dump(),
                    "ship_command_points": ship_class.command_points,
                }
                for i, ship_class in enumerate(self.ship_class)
            ]
        ).set_index("ship_class_id")

    @computed_field
    @property
    def ship_modules(self) -> pd.DataFrame:
        print("Creating ship modules df")
        df = pd.DataFrame(
            [
                {
                    "spaceship_module_name": ship_weapon,
                    "spaceship_module_power": ship_weapon_class["base_power"],
                    "spaceship_module_size": ship_weapon_size,
                }
                for ship_weapon_size, ship_weapon_class in self.ship_weapons.model_dump().items()
                for ship_weapon in ship_weapon_class["value"]
            ]
        )
        df["spaceship_module_id"] = df.index
        return df.set_index("spaceship_module_id")

    class Config:
        arbitrary_types_allowed = True


@lru_cache()
def ship_class_df() -> pd.DataFrame:
    return ships_info().ship_class_df


@lru_cache()
def ship_modules() -> pd.DataFrame:
    return ships_info().ship_modules


@lru_cache()
def ship_class_rank() -> dict[str, int]:
    """
    Converts the ship class name to a rank. Higher rank means better ship class.
    """
    return {
        ship_class: i
        for i, ship_class in enumerate(
            ship_class_df()["ship_class_name"].tolist()
        )
    }


@lru_cache()
def ships_info():
    ship_info_file = "./assets/ships.json"

    with open(os.path.join(get_location(), ship_info_file), "r") as f:
        print(f"Loading {ship_info_file}")
        ships = ShipsInfo(**json.load(f))

    return ships
