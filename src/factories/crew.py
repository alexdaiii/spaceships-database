import math
from functools import lru_cache

import networkx as nx
import numpy as np
import pandas as pd
from faker import Faker
from sqlalchemy import Engine, select, func, insert, update

import colorful as cf

from src.database.db import get_session
from src.factories.utils.empires_util import empires_info
from src.factories.utils.ships_empire_util import empire_fleet_info
from src.factories.utils.ships_util import ship_class_df
from src.models import (
    StarSystem,
    Planet,
    Biome,
    Crew,
    Spaceship,
    Fleet,
    ShipTemplate,
    ShipClass,
    CrewFriend,
)
from src.util import CURR_DATE, START_DATE, TIMEZONE


def add_crew(
    rng: np.random.Generator,
    fake: Faker,
    *,
    engine: Engine,
):
    print(cf.yellow("Adding crew..."))

    for i, ((_, e_gov_info), (_, e_fleet_info), num_subordinates) in enumerate(
        zip(
            empires_info(engine).iterrows(),
            empire_fleet_info(engine, rng).iterrows(),
            rng.integers(2, 11, size=len(empires_info(engine))),
        )
    ):
        print(f"Adding crew for empire {i + 1}/{len(empires_info(engine))}")
        for _, ship_class in ship_class_df().iterrows():
            add_empire_crew(
                engine,
                fake=fake,
                rng=rng,
                gov_info=e_gov_info,
                fleet_info=e_fleet_info,
                ship_class=ship_class,
            )

        print(
            f"Adding crew relationships for empire "
            f"{i + 1}/{len(empires_info(engine))}"
        )
        add_crew_relationships(
            engine,
            rng,
            empire_id=e_fleet_info["empire_id"],
            num_subordinates=num_subordinates,
        )


@lru_cache(maxsize=1)
def get_crew_planets(engine: Engine, *, empire_id: int, pct_foreign: float):
    with get_session(engine) as session:
        crew_planet_ids = session.scalars(
            select(Planet.planet_id)
            .join(
                StarSystem,
            )
            .join(Biome)
            .where(StarSystem.empire_owner == empire_id)
            .where(Biome.biome_is_habitable == True)
        ).all()
        num_foreign_planets = int(len(crew_planet_ids) * pct_foreign)

        # randomly order
        foreign_planets = session.scalars(
            select(Planet.planet_id)
            .join(Biome)
            .where(Biome.biome_is_habitable == True)
            .order_by(func.random())
            .limit(num_foreign_planets)
        ).all()

    return crew_planet_ids + foreign_planets


def get_empire_ships(engine: Engine, *, empire_id: int, ship_class_id: int):
    return pd.read_sql(
        select(Spaceship.spaceship_id)
        .join(Fleet)
        .join(ShipTemplate)
        .join(ShipClass)
        .where(Fleet.fleet_empire_owner == empire_id)
        .where(ShipClass.ship_class_id == ship_class_id),
        engine,
    )


def add_empire_crew(
    engine: Engine,
    *,
    fake: Faker,
    rng: np.random.Generator,
    gov_info: pd.Series,
    fleet_info: pd.Series,
    ship_class: pd.Series,
):
    num_ships = fleet_info[f"num_{ship_class['ship_class_name']}"]

    if num_ships == 0:
        return

    with get_session(engine) as session:
        session.execute(
            insert(Crew),
            crew_val_helper(
                fake,
                rng,
                planets=get_crew_planets(
                    engine,
                    empire_id=fleet_info["empire_id"],
                    pct_foreign=gov_info["expansion_score"] / 100,
                ),
                crew_per_ship=ship_class["ship_crew"],
                ships=get_empire_ships(
                    engine,
                    empire_id=fleet_info["empire_id"],
                    ship_class_id=ship_class.name,
                ),
            ),
        )


def crew_val_helper(
    fake: Faker,
    rng: np.random.Generator,
    *,
    planets: list[int],
    crew_per_ship: int,
    ships: pd.DataFrame,
):
    for ship_id in ships["spaceship_id"]:
        for _ in range(crew_per_ship):
            birth = fake.date_time_between(
                start_date=START_DATE, end_date=CURR_DATE, tzinfo=TIMEZONE
            )
            hire = fake.date_time_between(
                start_date=birth, end_date=CURR_DATE, tzinfo=TIMEZONE
            )
            yield {
                "crew_name": fake.name(),
                "planet_of_birth_id": int(rng.choice(planets)),
                "spaceship_id": ship_id,
                "birth_date": birth,
                "hire_date": hire,
                "command_points": ((CURR_DATE - hire).days // 365),
            }


def get_empire_crew(engine: Engine, *, empire_id: int):
    return pd.read_sql(
        select(Crew.crew_id)
        .join(Spaceship)
        .join(Fleet)
        .where(Fleet.fleet_empire_owner == empire_id),
        engine,
    )


def add_crew_relationships(
    engine: Engine,
    rng: np.random.Generator,
    *,
    empire_id: int,
    num_subordinates: int,
):
    crew = get_empire_crew(engine, empire_id=empire_id)

    with get_session(engine) as session:
        # update the crew table with new crew relationships
        session.execute(
            update(Crew),
            create_reports_to(
                crew,
                rng,
                num_subordinates=num_subordinates,
            ),
        )
        session.execute(
            insert(CrewFriend),
            create_friends_graph(
                crew,
                rng,
            ),
        )


def node_to_crew_map(
    rng: np.random.Generator,
    crew_ids: pd.Series,
    g: nx.Graph,
):
    return {
        node: crew_id
        for crew_id, node in zip(
            rng.choice(crew_ids, size=len(crew_ids), replace=False),
            g,
        )
    }


def create_reports_to(
    crew: pd.DataFrame,
    rng: np.random.Generator,
    *,
    num_subordinates: int,
):
    """
    Creates a balanced n-ry tree that determines the crew hierarchy
    """
    max_depth = math.ceil(math.log(len(crew), num_subordinates))

    g = nx.balanced_tree(num_subordinates, max_depth, nx.DiGraph)

    # map crew_id to node and remove nodes that don't have crew
    node_to_crew = node_to_crew_map(
        rng,
        crew["crew_id"],
        g,
    )

    report_to_update = []

    for node in node_to_crew:
        manager = list(g.predecessors(node))

        if len(manager) == 0:
            continue

        report_to_update.append(
            {
                "crew_id": int(node_to_crew[node]),
                "reports_to": int(node_to_crew[manager[0]]),
            }
        )

    return report_to_update


def create_friends_graph(
    crew: pd.DataFrame,
    rng: np.random.Generator,
):
    """
    Creates a dorogovtsev_goltsev_mendes_graph of size
    ceil(log_3(len(crew) / 3 - 1))
    """
    dgmg_n = math.ceil(math.log(len(crew) / 3 - 1, 3))

    g = nx.dorogovtsev_goltsev_mendes_graph(n=dgmg_n)

    node_to_crew = node_to_crew_map(
        rng,
        crew["crew_id"],
        g,
    )

    for node in node_to_crew:
        for neighbor in g.neighbors(node):
            yield {
                "crew_id": int(node_to_crew[node]),
                "friend_id": int(node_to_crew[neighbor]),
            }


__all__ = ["add_crew"]
