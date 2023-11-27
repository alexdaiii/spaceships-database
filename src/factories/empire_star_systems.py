import math
from functools import lru_cache

import colorful as cf
import numpy as np
import pandas as pd
from sqlalchemy import Engine, delete, select, update

from src.database.db import get_session
from src.factories.empires_util import empire_id_range, empires_info, ethic_df
from src.models import Biome, Empire, Planet, StarSystem

_h_planet_page_size = 1000


@lru_cache(maxsize=3)
def get_habitable_planets(engine: Engine, page: int = 0):
    print(cf.yellow("Getting habitable planets..."))

    planets_stmt = (
        select(StarSystem.star_system_id)
        .distinct()
        .join(Planet)
        .join(Biome)
        .filter(Biome.biome_is_habitable == True)
        .order_by(StarSystem.star_system_id)
        .limit(_h_planet_page_size)
        .offset(page * _h_planet_page_size)
    )
    df = pd.read_sql_query(planets_stmt, con=engine)

    return df


def remove_excess_empires(engine: Engine):
    """
    Removes all empires with no star systems.

    REQUIRES ON DELETE CASCADE on EmpireToEthic N:M table.
    """
    with get_session(engine) as session:
        deleted_empires = session.execute(
            delete(Empire).where(
                Empire.empire_id.notin_(
                    select(StarSystem.empire_owner)
                    .distinct()
                    .where(StarSystem.empire_owner != None)
                )
            )
        )
        print(
            cf.yellow(
                f"Deleted {deleted_empires.rowcount} empires with no star systems."
            )
        )


def assign_home_systems(
    engine: Engine, num_empires: int, rng: np.random.Generator
):
    num_pages = math.ceil(num_empires / _h_planet_page_size)
    min_id, max_id = empire_id_range(engine)
    empires = rng.choice(
        np.arange(min_id, max_id + 1), size=num_empires, replace=False
    )

    stars_to_empires = dict()
    for page, empires_idx in zip(
        range(num_pages), range(0, len(empires), _h_planet_page_size)
    ):
        habitable_stars = get_habitable_planets(engine, page=page)

        if len(habitable_stars) == 0:
            # means we've run out of habitable star systems
            break

        # NOTE: this end_idx is for slicing (not inclusive)
        end_idx = min(empires_idx + _h_planet_page_size, num_empires)
        empires_assign = empires[empires_idx:end_idx]
        num_to_assign = min(len(empires_assign), len(habitable_stars))

        stars_to_empires.update(
            dict(
                zip(
                    rng.choice(
                        habitable_stars.star_system_id.unique(),
                        size=num_to_assign,
                        replace=False,
                    ),
                    empires_assign,
                )
            )
        )

    save_home_systems(engine, stars_to_empires)
    # # remove excess empires
    remove_excess_empires(engine)


def save_home_systems(engine: Engine, stars_to_empires: dict[int, int]):
    with get_session(engine) as session:
        for star_system_id, empire_id in stars_to_empires.items():
            session.execute(
                update(StarSystem)
                .where(StarSystem.star_system_id == int(star_system_id))
                .values(empire_owner=int(empire_id))
            )


def add_empire_expansion_score(df: pd.DataFrame, rng: np.random.Generator):
    ethics = ethic_df()

    expansion_score = {
        val: i + 1
        for i, val in enumerate(
            rng.choice(ethics.index, size=len(ethics), replace=False)
        )
    }

    df["expansion_score"] = df.apply(
        lambda row: sum(
            expansion_score[ethic_id] * ethic_attraction
            for ethic_id, ethic_attraction in zip(
                row["empire_ethic_id"], row["empire_ethic_attraction"]
            )
        ),
        axis=1,
    )

    return df


def assign_num_systems(
    df: pd.DataFrame,
    rng: np.random.Generator,
    num_stars: int,
    num_empires: int,
):
    settlement_score = 0.7
    base_settled_systems = num_stars * settlement_score
    base_unsettled_systems = num_stars * (1 - settlement_score)

    rand_error = rng.normal(
        0, base_unsettled_systems / (num_empires * 2), size=num_empires
    )

    df["num_systems"] = (
        df["expansion_score"]
        / df["expansion_score"].sum()
        * base_settled_systems
        + rand_error
    ).astype(int) - 1

    # make sure sum of num_systems is <= num_stars
    num_owned_systems = df["num_systems"].sum()

    if num_owned_systems >= num_stars:
        # too many systems
        print(
            cf.orange(
                "Empires own too many stars! Removing systems from owners"
            )
        )
        overage = (num_owned_systems - num_stars) * 2
        df["num_systems"] = df["num_systems"] - math.ceil(
            overage / num_empires
        )

    return df


def update_empire_stars(
    engine: Engine, empire_df: pd.DataFrame, rng: np.random.Generator
):
    with get_session(engine) as session:
        avaliable_ids = (
            session.execute(
                select(StarSystem.star_system_id).where(
                    StarSystem.empire_owner == None
                )
            )
            .scalars()
            .all()
        )
        assigned_systems_order = rng.choice(
            avaliable_ids, size=empire_df["num_systems"].sum(), replace=False
        ).tolist()

        start_id = 0
        for empire_id, num_systems in empire_df[
            ["empire_id", "num_systems"]
        ].values:
            end_id = start_id + num_systems
            session.execute(
                update(StarSystem)
                .where(
                    StarSystem.star_system_id.in_(
                        assigned_systems_order[start_id:end_id]
                    )
                )
                .values(empire_owner=int(empire_id))
            )
            start_id = end_id


def assign_empire_star_systems(
    rng: np.random.Generator,
    *,
    engine: Engine,
    num_stars: int,
    num_empires: int,
):
    assign_home_systems(engine, num_empires, rng)

    empires = add_empire_expansion_score(empires_info(engine), rng)

    empires = assign_num_systems(empires, rng, num_stars, num_empires)

    update_empire_stars(engine, empires, rng)


__all__ = [
    "assign_empire_star_systems",
]
