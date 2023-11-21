import math

import colorful as cf
import numpy as np
import pandas as pd
from faker import Faker
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import Engine, insert, select

from src.database.db import get_session
from src.models import Biome, Planet, StarSystem

from .celestial_bodies_util import biomes_df, stars_type_df, load_star_config
from .utils import MAX_PLANET_SIZE, MIN_PLANET_SIZE
from ..settings import get_settings
from ..util import MIN_NUM_STARS, MAX_NUM_STARS


def add_biomes(engine: Engine):
    with get_session(engine) as session:
        session.execute(
            insert(Biome),
            biomes_df().reset_index().to_dict("records"),
        )


def create_planets(
    *,
    rng: np.random.Generator,
    engine: Engine,
):
    print(cf.yellow("Generating planets..."))

    add_biomes(engine)

    scaler = MinMaxScaler(feature_range=(MIN_PLANET_SIZE, MAX_PLANET_SIZE))

    stars_type_df().apply(
        add_planets, axis=1, engine=engine, rng=rng, scaler=scaler
    )

    add_structures(engine, rng, target="special")
    add_structures(engine, rng, target="megastructure")


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
    rock = 199 * (1 + habitability_score) * load_star_config().habitable_worlds

    gas_mult = max(int((gas + large_rock) / rock + rng.uniform(-5, 5)), 0)

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


def get_biomes_by_size(df: pd.DataFrame, size: int):
    return df[(df["min_size"] <= size) & (df["max_size"] >= size)]


def apply_planet_biomes(
    df: pd.DataFrame, rng: np.random.Generator, star_habitability: float
):
    non_special_biomes = biomes_df()[biomes_df()["gen_type"] == "normal"]

    for size in range(MIN_PLANET_SIZE, MAX_PLANET_SIZE + 1):
        choice = get_biomes_by_size(non_special_biomes, size)

        if len(choice) == 0:
            raise ValueError(f"No biomes found for size {size}")

        df.loc[df["planet_size"] == size, "planet_biome"] = rng.choice(
            choice.index, size=sum(df["planet_size"] == size), replace=True
        )

    df["planet_biome"] = df["planet_biome"].astype(int)

    return df


# def apply_special_biomes(
#     df: pd.DataFrame,
#     *,
#     rng: np.random.Generator,
#     special_biomes: pd.DataFrame,
#     size: int,
# ):
#     # perform bernoulli trial for each planet
#     # if true, set biome to special biome - if more than one special biome - the last biome while iterating
#     # will be the biome set
#     n_trials = df.shape[0]
#     # number of planets with size == size
#     n_planet_size = sum(df["planet_size"] == size)
#
#     min_exp = 1
#     max_exp = 1.25
#     slope = (max_exp - min_exp) / (MAX_NUM_STARS - MIN_NUM_STARS)
#     exponent = min_exp + slope * (get_settings().num_stars - MIN_NUM_STARS)
#
#     divisor = n_trials**exponent / n_planet_size
#
#     success = rng.binomial(
#         n=1,
#         p=special_biomes["special_gen_mean"].div(divisor).clip(0, 1),
#         size=(n_trials, len(special_biomes)),
#     )
#     # pad success with 0 where planet_size != size
#
#     for i, biome in enumerate(special_biomes.index):
#         df.loc[
#             (df["planet_size"] == size) & (success[:, i]), "planet_biome"
#         ] = biome
#
#     return df


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


def add_structures(engine: Engine, rng: np.random.Generator, *, target: str):
    """
    Post planet generation, add special planet types
    """

    mega = []

    for i, row in biomes_df()[biomes_df()["gen_type"] == target].iterrows():
        for size in range(row["min_size"], row["max_size"] + 1):
            mega.extend(
                [
                    {
                        "biome": row.name,
                        "size": size,
                    }
                    for _ in range(int(row["special_gen_mean"]))
                ]
            )

    if len(mega) == 0:
        return

    print(cf.yellow(f"Generating {target} celestial bodies..."))

    with get_session(engine) as session:
        num_planets = session.query(Planet).count()

        selected_ids = (
            rng.choice(
                num_planets,
                size=len(mega),
                replace=False,
            )
            + 1
        ).tolist()

        planets = session.scalars(
            select(Planet).where(Planet.planet_id.in_(selected_ids))
        ).all()

        for planet, mega_info in zip(planets, mega):
            planet.planet_biome = mega_info["biome"]
            planet.planet_size = mega_info["size"]


__all__ = ["create_planets"]
