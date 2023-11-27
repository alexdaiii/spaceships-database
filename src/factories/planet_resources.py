import colorful as cf
import numpy as np
import pandas as pd
from sqlalchemy import Engine, select

from .empires_util import empires_info, authority_df
from src.database.db import get_session
from src.models import Planet, StarSystem, Empire, Biome
from .utils import MIN_PLANET_SIZE, MAX_PLANET_SIZE
from ..util import get_m_and_b


def add_auth_rank(df: pd.DataFrame, *, rng: np.random.Generator):
    auth_rank = {
        auth_id: i
        for i, auth_id in enumerate(
            rng.choice(
                authority_df().index, size=len(authority_df()), replace=False
            )
        )
    }

    df["gov_efficiency_bonus"] = df["empire_authority_id"].map(auth_rank)
    df["gov_efficiency"] = df["gov_efficiency_bonus"] / len(auth_rank)

    return df


def get_habitable_planets_pops(
    engine: Engine,
    empire: pd.Series,
    rng: np.random.Generator,
    *,
    m: float,
    b: float,
    scale: float
):
    # get the habitable planets for this empire
    habitable_planets = pd.read_sql(
        select(
            Planet.planet_id,
            Planet.planet_size,
            Planet.planet_energy_value,
            Planet.planet_minerals_value,
            Planet.planet_research_value,
            Planet.planet_trade_value,
        )
        .join(StarSystem)
        .join(Biome)
        .where(Biome.biome_is_habitable == True)
        .where(StarSystem.empire_owner == empire.empire_id),
        engine,
    )

    habitable_planets["planet_pops"] = (
        (habitable_planets["planet_size"] * m + b)
        + empire.gov_efficiency_bonus * scale
        + rng.normal(0, scale, len(habitable_planets))
    ).astype(int)

    return habitable_planets


def add_habitable_planet_resources(df: pd.DataFrame, efficiency: float):
    # resources intrinsic to the planet
    df["planet_energy_value"] = (
        (df["planet_energy_value"] + 1) * df["planet_pops"] * 5 * efficiency
    ).astype(int)
    df["planet_minerals_value"] = (
        (df["planet_minerals_value"] + 1) * df["planet_pops"] * 10 * efficiency
    ).astype(int)

    # exponential growth - dependent on pops
    df["planet_research_value"] = (
        df["planet_research_value"] + (df["planet_pops"] * efficiency) ** 1.5
    ).astype(int)
    df["planet_trade_value"] = (
        (df["planet_trade_value"] + 1) + (df["planet_pops"] * efficiency) ** 2
    ).astype(int)

    return df


def add_planet_pops(rng: np.random.Generator, *, engine: Engine):
    print(cf.yellow("Adding planet pops"))

    empires = add_auth_rank(
        empires_info(engine),
        rng=rng,
    )

    min_pops = 15
    max_pops = 100

    m, b = get_m_and_b(
        x1=MIN_PLANET_SIZE,
        y1=min_pops,
        x2=MAX_PLANET_SIZE,
        y2=max_pops,
    )

    scale = 2.5

    # loop through each empire's habitable planets
    # (w 100K stars only about 50 planets max) so no pagination needed
    for _, empire in empires.iterrows():
        habitable_planets = get_habitable_planets_pops(
            engine, empire, rng, m=m, b=b, scale=scale
        )

        habitable_planets = add_habitable_planet_resources(
            habitable_planets, empire.gov_efficiency
        )

        # update the planets
        with get_session(engine) as session:
            session.bulk_update_mappings(
                Planet,
                habitable_planets.to_dict(orient="records"),
            )


__all__ = ["add_planet_pops"]
