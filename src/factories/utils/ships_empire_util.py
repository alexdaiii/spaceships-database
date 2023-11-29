from functools import lru_cache

import numpy as np
import pandas as pd
from sqlalchemy import Engine

from .empires_util import empires_info
from .ships_util import ship_class_df, ship_class_rank


# TODO: many of these names are hard coded - should rely on the config files
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
    df["num_titan"] = df.apply(
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

    # remainder of command limit is corvettes
    df["num_corvette"] = (
        df["command_limit"]
        - (
            df["num_titan"]
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

    capital_a = ord("A")
    capital_z = ord("Z")

    # random 3 capital letter prefix
    df["empire_ship_prefix"] = [
        "".join([chr(c) for c in row])
        for row in rng.integers(capital_a, capital_z + 1, size=(len(df), 3))
    ]

    df["total_ships"] = (
        df["num_titan"]
        + df["num_juggernaut"]
        + df["num_colossus"]
        + df["num_star_eater"]
        + df["num_battleship"]
        + df["num_cruiser"]
        + df["num_destroyer"]
        + df["num_frigate"]
        + df["num_corvette"]
    )

    return df
