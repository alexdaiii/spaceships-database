import json
from functools import lru_cache

import colorful as cf
import numpy as np
import pandas as pd
from sqlalchemy import Engine, insert, select

from src.database.db import get_session
from src.factories.empires_util import empires_info
from src.factories.ships_util import (
    ship_class_df,
    ships_info,
    ship_modules,
    ship_class_rank,
)
from src.models import ShipClass, Fleet, SpaceshipModule
from src.util import df_info


def calculate_special_fleet_comp(df: pd.DataFrame) -> pd.DataFrame:
    def calc_ship_limit(
        df_app: pd.DataFrame,
        ship_class: str,
        command_limit_req: int,
        max_clamp: int = np.inf,
    ):
        return (
            min(df_app["command_limit"] // command_limit_req, max_clamp)
            if df_app["max_ship_class_rank"] >= ship_class_rank()[ship_class]
            else 0
        )

    df["num_star_eater"] = df.apply(
        calc_ship_limit,
        axis=1,
        args=("star_eater", 1, 1),
    )
    df["num_colossus"] = df.apply(
        calc_ship_limit,
        axis=1,
        args=("colossus", 160),
    )
    df["num_juggernaut"] = df.apply(
        calc_ship_limit,
        axis=1,
        args=("juggernaut", 80),
    )
    df["num_titans"] = df.apply(
        calc_ship_limit,
        axis=1,
        args=("titan", 20),
    )

    return df


def calculate_regular_fleet_comp(
    df: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    min_pct = 3.125

    def calc_ship_limit(
        df_app: pd.Series,
        ship_class: str,
        pct: float,
    ):
        pct += rng.normal(0, 0.125)

        return (
            int(df_app["command_limit"] * (pct / 100))
            if df_app["max_ship_class_rank"] >= ship_class_rank()[ship_class]
            else 0
        )

    df["num_battleship"] = df.apply(
        calc_ship_limit,
        axis=1,
        args=("battleship", min_pct),
    )
    df["num_cruiser"] = df.apply(
        calc_ship_limit,
        axis=1,
        args=("cruiser", min_pct * 2),
    )
    df["num_destroyer"] = df.apply(
        calc_ship_limit,
        axis=1,
        args=("destroyer", min_pct * 4),
    )
    df["num_frigate"] = df.apply(
        calc_ship_limit,
        axis=1,
        args=("frigate", min_pct * 8),
    )

    print(np.ceil(df["command_limit"].mean() / 10))

    # remainder of command limit is corvettes
    df["num_corvette"] = (
        df["command_limit"]
        - (
            df["num_titans"]
            + df["num_juggernaut"]
            + df["num_colossus"]
            + df["num_star_eater"]
            + df["num_battleship"]
            + df["num_cruiser"]
            + df["num_destroyer"]
            + df["num_frigate"]
            + rng.integers(
                0, max(np.ceil(df["command_limit"].mean() / 10), 2), len(df)
            )
        )
    ).clip(0)
    # clamp corvettes to min 0
    return df


@lru_cache()
def empire_fleet_info(engine: Engine, rng: np.random.Generator):
    df = empires_info(engine)[
        ["empire_id", "total_fleets", "max_fleet_size"]
    ].copy()
    df["command_limit"] = df["total_fleets"] * df["max_fleet_size"]
    # create len(ship_class_df()) buckets and assign each empire to a
    # bucket based on total command limit
    df["max_ship_class"] = pd.cut(
        df["command_limit"],
        len(ship_class_df()),
        labels=ship_class_df()["ship_class_name"].tolist(),
    )
    df["max_ship_class_rank"] = df["max_ship_class"].map(ship_class_rank())

    df = calculate_special_fleet_comp(df)
    df = calculate_regular_fleet_comp(df, rng)

    df["total_ships"] = (
        df["num_titans"]
        + df["num_juggernaut"]
        + df["num_colossus"]
        + df["num_star_eater"]
        + df["num_battleship"]
        + df["num_cruiser"]
        + df["num_destroyer"]
        + df["num_frigate"]
        + df["num_corvette"]
    )

    df_info(df)

    return df


def get_fleets_by_empire_id(engine: Engine, *, empire_id: int):
    return pd.read_sql(select(Fleet).where(Fleet.empire == empire_id), engine)


def add_fleet_ships(rng: np.random.Generator, *, engine: Engine):
    add_ship_classes(engine)
    add_ship_mods(engine)

    empire_fleets = empire_fleet_info(engine, rng)

    print(cf.blue(f"Adding {empire_fleets['total_ships'].sum()} ships"))

    for _, empire in empire_fleets.iterrows():
        print(f"Adding ships for empire {empire.empire_id}")
        add_ships(
            rng,
            empire_id=empire.empire_id,
            num_ships=empire.command_limit,
            max_ship_class=empire.max_ship_class,
            engine=engine,
        )

        if empire.empire_id > 1:
            break


def add_ships(
    rng: np.random.Generator,
    *,
    empire_id: int,
    num_ships: int,
    max_ship_class: str,
    engine: Engine,
):
    ...


def add_ship_classes(engine: Engine):
    print(cf.yellow("Adding ship classes"))

    with get_session(engine) as session:
        session.execute(
            insert(ShipClass), ship_class_df().reset_index().to_dict("records")
        )


def add_ship_mods(engine: Engine):
    print(cf.yellow("Adding ship modules"))

    df_info(ship_modules())

    with get_session(engine) as session:
        session.execute(
            insert(SpaceshipModule),
            ship_modules().reset_index().to_dict("records"),
        )
