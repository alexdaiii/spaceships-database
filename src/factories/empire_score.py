import colorful as cf
import pandas as pd
from sqlalchemy import Engine, func, select, update

from src.database.db import get_session
from src.factories.utils.empires_util import empires_info, get_empire_resources
from src.factories.utils.ships_util import ship_class_df
from src.models import (Biome, Empire, Fleet, Planet, ShipTemplate,
                        ShipTemplateModule, Spaceship, SpaceshipModule,
                        SpaceshipRank, StarSystem)
from src.util import df_info


def calculate_empire_score(engine: Engine, rng):
    print(cf.yellow("Calculating empire score..."))

    scores_df = get_empire_info_df(engine)

    scores_df["empire_score"] = (
        # economic strength
        scores_df["total_energy"]
        + scores_df["total_minerals"]
        # technology
        + scores_df["total_research"] * 6
        # economy
        + scores_df["total_trade"]
        # expansion
        + scores_df["num_systems"] * 10000
        + scores_df["colonies_count"] * 50000
        + scores_df["num_pops"] * 20000
        # fleet power
        + scores_df["fleet_power"]
    )

    with get_session(engine) as session:
        session.execute(
            update(Empire),
            scores_df[["empire_id", "empire_score"]].to_dict(orient="records"),
        )


def get_empire_info_df(engine: Engine):
    scores_df = get_empire_resources(engine).sort_values(by="empire_id")

    scores_df = scores_df.merge(
        empires_info(engine)[["empire_id", "num_systems"]], on="empire_id"
    )
    scores_df = colonies_info(engine, scores_df)
    scores_df = fleet_info(engine, scores_df)

    return scores_df


def colonies_info(engine: Engine, scores_df: pd.DataFrame) -> pd.DataFrame:
    emp_planets_info = pd.read_sql(
        select(
            Empire.empire_id,
            func.count(Planet.planet_id).label("colonies_count"),
            func.sum(Planet.planet_pops).label("num_pops"),
        )
        .select_from(Empire)
        .join(StarSystem)
        .join(Planet)
        .join(Biome)
        .where(Biome.biome_is_habitable == True)
        .group_by(Empire.empire_id)
        .order_by(Empire.empire_id),
        engine,
    )

    # join the scores_df with the emp_planets_info
    scores_df = scores_df.merge(emp_planets_info, on="empire_id")

    return scores_df


def fleet_info(engine: Engine, scores_df: pd.DataFrame) -> pd.DataFrame:
    xp_info = pd.read_sql(select(SpaceshipRank), engine)

    df_power = scores_df[["empire_id"]].copy()

    for _, rank in xp_info.iterrows():
        for _, ship_class in ship_class_df().iterrows():
            label = f"{rank.spaceship_rank_name}_{ship_class.ship_class_name}_power"

            empires_ships = pd.read_sql(
                select(
                    Empire.empire_id,
                    func.sum(
                        ShipTemplateModule.ship_module_count
                        * SpaceshipModule.spaceship_module_power
                        * (1 + rank.spaceship_bonus_power)
                    ).label(label),
                )
                .join(Fleet)
                .join(Spaceship)
                .join(ShipTemplate)
                .join(ShipTemplateModule)
                .join(SpaceshipModule)
                .where(
                    Spaceship.spaceship_experience
                    >= rank.spaceship_min_experience,
                )
                .where(
                    Spaceship.spaceship_experience
                    < rank.spaceship_max_experience,
                )
                .where(
                    ShipTemplate.ship_class_id == ship_class.name,
                )
                .group_by(Empire.empire_id),
                engine,
            )

            df_power = df_power.merge(
                empires_ships, on="empire_id", how="left"
            )

    # fill any NaNs with 0
    df_power = df_power.fillna(0)
    # add the power columns together
    df_power["fleet_power"] = df_power.sum(axis=1) - df_power["empire_id"]

    # merge the power columns with the scores_df
    scores_df = scores_df.merge(
        df_power[["empire_id", "fleet_power"]], on="empire_id"
    )

    return scores_df
