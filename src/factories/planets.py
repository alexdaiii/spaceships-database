import json
import math
import os
from functools import lru_cache
from typing import Literal

import colorful as cf
import numpy as np
import pandas as pd
from faker import Faker
from pydantic import BaseModel, computed_field, Field
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import Engine, insert

from ..database.db import get_session
from ..models import StarSystem, Biome, Planet
from ..util import get_location
from .stars import stars_type_df
from .utils import STARTING_ID, MIN_PLANET_SIZE, MAX_PLANET_SIZE


class BiomeConfig(BaseModel):
    name: str
    average_temperature: int
    average_humidity: int
    biome_is_habitable: bool
    materials: list[Literal["minerals", "energy", "research", "trade_value"]]
    min_size: int = Field(ge=MIN_PLANET_SIZE, le=MAX_PLANET_SIZE)
    max_size: int = Field(ge=MIN_PLANET_SIZE, le=MAX_PLANET_SIZE)
    gen_type: Literal["normal", "special"] = Field("normal")


class PlanetsConfig(BaseModel):
    biomes: list[BiomeConfig]

    @computed_field
    @property
    def biomes_df(self) -> pd.DataFrame:
        print(cf.yellow("Creating biomes dataframe..."))

        return pd.DataFrame(
            [
                {
                    "biome_id": i,
                    "biome_name": biome.name,
                    "average_temperature": biome.average_temperature,
                    "average_humidity": biome.average_humidity,
                    "biome_is_habitable": biome.biome_is_habitable,
                    "biome_materials": biome.materials,
                    "min_size": biome.min_size,
                    "max_size": biome.max_size,
                    "gen_type": biome.gen_type,
                }
                for i, biome in enumerate(self.biomes, start=STARTING_ID)
            ]
        ).set_index("biome_id")

    class Config:
        arbitrary_types_allowed = True


@lru_cache()
def load_planet_config():
    planet_conf_file = "assets/planets.json"

    with open(os.path.join(get_location(), planet_conf_file)) as f:
        return PlanetsConfig(**json.load(f))


@lru_cache()
def biomes_df():
    return load_planet_config().biomes_df


def add_biomes(engine: Engine):
    with get_session(engine) as session:
        session.execute(
            insert(Biome),
            biomes_df().reset_index().to_dict("records"),
        )


def create_planets(
    *,
    fake: Faker,
    rng: np.random.Generator,
    engine: Engine,
):
    print(cf.yellow("Generating planets..."))

    add_biomes(engine)

    scaler = MinMaxScaler(feature_range=(MIN_PLANET_SIZE, MAX_PLANET_SIZE))

    stars_type_df().apply(
        add_planets, axis=1, engine=engine, rng=rng, scaler=scaler
    )


def get_num_stars_by_type(type_id: int, engine: Engine):
    with get_session(engine) as session:
        return (
            session.query(StarSystem)
            .filter(StarSystem.star_type_id == type_id)
            .count()
        )


def get_stars_by_page(
    engine: Engine, *, type_id: int, page: int, page_size: int
):
    """
    Returns a list of star ids for a given star type id and page number
    """
    with get_session(engine) as session:
        return (
            session.query(
                StarSystem.star_system_id, StarSystem.star_system_name
            )
            .filter(StarSystem.star_type_id == type_id)
            .offset(page * page_size)
            .limit(page_size)
            .all()
        )


def get_planet_sizes(
    scaler: MinMaxScaler,
    rng: np.random.Generator,
    num_planets: int,
    habitability_score: float,
):
    rock_mu = 1 + rng.uniform(-0.5, 0.5)
    sigma = 0.5 + rng.uniform(0, 0.25, size=2)
    sep = 3.5 + rng.uniform(0, 0.75)

    # from NASA number of planets discovered (heavily biased towards gas giants)
    gas = 3658
    large_rock = 1675
    rock = 199 * (1 + habitability_score)

    gas_mult = int((gas + large_rock) / rock + rng.uniform(-5, 5))

    n_sample_per_dist = math.ceil(num_planets / (1 + gas_mult))

    return scaler.fit_transform(
        np.concatenate(
            (
                rng.normal(
                    loc=rock_mu, scale=sigma[0], size=n_sample_per_dist
                ),
                np.repeat(
                    rng.normal(
                        loc=rock_mu + sep,
                        scale=sigma[1],
                        size=n_sample_per_dist,
                    ),
                    gas_mult,
                ),
            )
        ).reshape(-1, 1)
    ).astype(int)[:num_planets]


def apply_planet_name(
    df: pd.DataFrame, star_habitability: float, rng: np.random.Generator
):
    df["planet_name"] = [
        f"{df.name}-{chr(ord('a') + i)}" for i in range(len(df))
    ]

    return df


def make_planet_df(
    *,
    rng: np.random.Generator,
    scaler: MinMaxScaler,
    num_planets: int,
    stars_ids: list[int],
    star_habitability: float,
):
    planets_df = pd.DataFrame(
        np.concatenate(
            (
                rng.choice(stars_ids, size=num_planets, replace=True),
                get_planet_sizes(
                    scaler, rng, num_planets, star_habitability
                ).reshape(-1, 1),
            ),
            axis=1,
        ),
        columns=["planet_star_system", "star_name", "planet_size"],
    )
    planets_df = fix_planet_size(planets_df)
    planets_df = apply_planet_biomes(planets_df, rng, star_habitability)

    planets_df = planets_df.groupby("star_name").apply(
        apply_planet_name, rng=rng, star_habitability=star_habitability
    )

    return planets_df


def fix_planet_size(df: pd.DataFrame):
    df["planet_size"] = df["planet_size"].astype(int)
    # for planet size < 2, set to 2
    df.loc[df["planet_size"] < 2, "planet_size"] = 2
    df.loc[df["planet_size"] > 25, "planet_size"] = 25

    return df


def apply_planet_biomes(
    df: pd.DataFrame, rng: np.random.Generator, star_habitability: float
):
    non_special_biomes = biomes_df()[biomes_df()["gen_type"] == "normal"]

    for size in range(MIN_PLANET_SIZE, MAX_PLANET_SIZE + 1):
        choice = non_special_biomes[
            (non_special_biomes["min_size"] <= size)
            & (non_special_biomes["max_size"] >= size)
        ]

        df.loc[df["planet_size"] == size, "planet_biome"] = rng.choice(
            choice.index, size=sum(df["planet_size"] == size), replace=True
        )
    df["planet_biome"] = df["planet_biome"].astype(int)

    return df


def add_planets(
    row: pd.Series,
    engine: Engine,
    rng: np.random.Generator,
    scaler: MinMaxScaler,
):
    star_id = int(row.name)
    num_stars_with_id = get_num_stars_by_type(star_id, engine)

    page_size = 1000

    for page in range((num_stars_with_id // page_size) + 1):
        print(
            f"Generating planets for star type {star_id} page {page} / {num_stars_with_id // page_size}"
        )

        stars_ids = get_stars_by_page(
            engine, type_id=star_id, page=page, page_size=page_size
        )

        num_planets = int(len(stars_ids) * row["mean_celestial_bodies"])

        if num_planets == 0:
            continue

        planets_df = make_planet_df(
            rng=rng,
            scaler=scaler,
            num_planets=num_planets,
            stars_ids=stars_ids,
            star_habitability=row["star_type_habitability"],
        )

        with get_session(engine) as session:
            session.execute(
                insert(Planet),
                planets_df.to_dict("records"),
            )
