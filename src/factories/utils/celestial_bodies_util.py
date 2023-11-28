import json
import os
from functools import lru_cache
from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field, computed_field

from src.util import get_location

from .util import MAX_PLANET_SIZE, MIN_PLANET_SIZE, STARTING_ID


class StarClass(BaseModel):
    name: str
    weight: float
    habitability: float = Field(0, ge=0, le=1)
    mean_celestial_bodies: float = Field(ge=0, le=15)


class StarsConfig(BaseModel):
    star_type_weights: list[StarClass]
    habitable_worlds: float = Field(1, ge=0.25, le=5)

    @computed_field
    @property
    def star_types_df(self) -> pd.DataFrame:
        print("Creating star types dataframe...")

        total_weights = sum([star.weight for star in self.star_type_weights])

        return pd.DataFrame(
            [
                {
                    "star_type_id": i,
                    "star_type_name": star.name,
                    "star_type_weight": star.weight,
                    "star_type_habitability": star.habitability,
                    "star_type_weight_pct": star.weight / total_weights,
                    "mean_celestial_bodies": star.mean_celestial_bodies,
                }
                for i, star in enumerate(
                    self.star_type_weights, start=STARTING_ID
                )
            ]
        ).set_index("star_type_id")

    class Config:
        arbitrary_types_allowed = True


@lru_cache()
def stars_type_df():
    return load_star_config().star_types_df


@lru_cache()
def load_star_config():
    stars_config_file = "../assets/stars.json"

    with open(os.path.join(get_location(), stars_config_file), "r") as f:
        print(f"Loading {stars_config_file}")
        stars_config = StarsConfig(**json.load(f))

    return stars_config


class BiomeConfig(BaseModel):
    name: str
    biome_is_habitable: bool
    materials: list[Literal["minerals", "energy", "research", "trade"]]
    min_size: int = Field(ge=MIN_PLANET_SIZE, le=MAX_PLANET_SIZE)
    max_size: int = Field(ge=MIN_PLANET_SIZE, le=MAX_PLANET_SIZE)
    gen_type: Literal["normal", "special", "megastructure"] = Field("normal")
    special_gen_mean: float = Field(0, ge=0)


class PlanetsConfig(BaseModel):
    biomes: list[BiomeConfig]

    @computed_field
    @property
    def biomes_df(self) -> pd.DataFrame:
        print("Creating biomes dataframe...")

        return pd.DataFrame(
            [
                {
                    "biome_id": i,
                    "biome_name": biome.name,
                    "biome_is_habitable": biome.biome_is_habitable,
                    "biome_materials": [
                        f"planet_{mat}_value" for mat in biome.materials
                    ],
                    "min_size": biome.min_size,
                    "max_size": biome.max_size,
                    "gen_type": biome.gen_type,
                    "special_gen_mean": biome.special_gen_mean,
                }
                for i, biome in enumerate(self.biomes, start=STARTING_ID)
            ]
        ).set_index("biome_id")

    class Config:
        arbitrary_types_allowed = True


@lru_cache()
def load_planet_config():
    planet_conf_file = "../assets/planets.json"

    with open(os.path.join(get_location(), planet_conf_file)) as f:
        return PlanetsConfig(**json.load(f))


@lru_cache()
def biomes_df():
    return load_planet_config().biomes_df
