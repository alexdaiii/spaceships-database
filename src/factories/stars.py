import json
import os
from functools import lru_cache

import colorful as cf
import numpy as np
import pandas as pd
from faker import Faker
from pydantic import BaseModel, Field, computed_field
from sqlalchemy import Engine, insert

from src.database.db import get_session
from src.factories.utils import STARTING_ID, load_file
from src.models.star_system import StarSystem, StarType
from src.util import get_location


class StarClass(BaseModel):
    name: str
    weight: float
    habitability: float = Field(0, min=0, max=1)
    mean_celestial_bodies: float = Field(min=0, max=15)


class StarsConfig(BaseModel):
    star_type_weights: list[StarClass]
    hyperlane_density: float = Field(min=0.25, max=5)

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
    stars_config_file = "assets/stars.json"

    with open(os.path.join(get_location(), stars_config_file), "r") as f:
        print(f"Loading {stars_config_file}")
        stars_config = StarsConfig(**json.load(f))

    return stars_config


def load_star_prefix():
    star_prefix = "assets/stars_prefix.txt"

    return load_file(get_location(), star_prefix)


def create_star_types(
    engine: Engine,
):
    print(cf.yellow("Adding star types..."))

    with get_session(engine) as session:
        session.execute(
            insert(StarType), stars_type_df().reset_index().to_dict("records")
        )


def create_stars(
    *,
    fake: Faker,
    rng: np.random.Generator,
    engine: Engine,
    num_stars: int,
):
    print(cf.yellow("Generating stars..."))

    create_star_types(engine)

    # TODO: MAKE IT INCREMENT BASED ON PAGE SIZE!!!
    page_size = 1000
    max_star_base = len(load_star_prefix())
    star_base_names = fake.words(
        nb=min(num_stars // 10, max_star_base),
        unique=True,
        ext_word_list=load_star_prefix(),
    )

    for i in range(1, num_stars + 1, len(star_base_names)):
        add_stars(
            engine=engine,
            rng=rng,
            i=i,
            star_base_names=star_base_names,
            num_stars=num_stars,
        )

    if engine.name == "mysql" or engine.name == "mariadb":
        raise NotImplementedError


def add_stars(
    *,
    engine: Engine,
    rng: np.random.Generator,
    i: int,
    star_base_names: list[str],
    num_stars: int,
):
    star_ids = stars_type_df().index
    star_id_weights = stars_type_df()["star_type_weight_pct"]

    j = i // len(star_base_names)

    sep = 50

    max_star_id = min(i + len(star_base_names) - 1, num_stars)
    num_stars_add = max_star_id - i + 1

    with get_session(engine) as session:
        session.execute(
            insert(StarSystem),
            [
                {
                    "star_system_name": f"{star_base_name}-{suffix}",
                    "star_type_id": star_type_id,
                }
                for star_base_name, star_type_id, suffix in zip(
                    star_base_names,
                    rng.choice(
                        star_ids,
                        size=num_stars_add,
                        p=star_id_weights,
                        replace=True,
                    ).tolist(),
                    rng.integers(
                        size=num_stars_add, low=j * sep + 1, high=j * sep + sep
                    ),
                )
            ],
        )


__all__ = [
    "create_stars",
]
