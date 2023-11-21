import math

import colorful as cf
import numpy as np
from faker import Faker
from sqlalchemy import Engine, insert

from src.database.db import get_session
from src.models.star_system import StarSystem, StarType
from src.util import get_location

from .celestial_bodies_util import stars_type_df
from .utils import load_file


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

    star_base_names = fake.words(
        nb=min(num_stars // 10, len(load_star_prefix()), 1000),
        unique=True,
        ext_word_list=load_star_prefix(),
    )

    page_size = len(star_base_names)
    num_pages = math.ceil(num_stars / page_size)

    for i in range(num_pages):
        if i == num_pages - 1 and num_stars % page_size != 0:
            page_size = num_stars % page_size

        add_stars(
            engine=engine,
            rng=rng,
            i=i,
            star_base_names=star_base_names,
            page_size=page_size,
        )


def add_stars(
    *,
    engine: Engine,
    rng: np.random.Generator,
    i: int,
    star_base_names: list[str],
    page_size: int,
):
    star_ids = stars_type_df().index
    star_id_weights = stars_type_df()["star_type_weight_pct"]

    sep = 50

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
                        size=page_size,
                        p=star_id_weights,
                        replace=True,
                    ).tolist(),
                    rng.integers(
                        size=page_size, low=i * sep + 1, high=i * sep + sep
                    ),
                )
            ],
        )


__all__ = [
    "create_stars",
]
