import colorful as cf
import numpy as np
import pandas as pd
from sqlalchemy import Engine, insert, select

from src.database.db import get_session
from src.models import Fleet, ShipClass, ShipTemplate, Spaceship
from src.util import get_location

from .utils.ships_empire_util import empire_fleet_info
from .utils.ships_util import ship_class_df
from .utils.util import load_file


def add_empire_ships(rng: np.random.Generator, *, engine: Engine):
    empire_fleets = empire_fleet_info(engine, rng)

    print(
        cf.blue(
            f"Adding {empire_fleets['total_ships'].sum()} ships to empires"
        )
    )

    for ship_class in ship_class_df()["ship_class_name"].unique():
        print(f"Adding {ship_class} ships to empires")
        for (_, empire), template in zip(
            empire_fleets.iterrows(),
            rng.choice(
                get_templates_by_class_type(engine, ship_class=ship_class)[
                    "ship_template_id"
                ],
                replace=True,
                size=len(empire_fleets),
            ),
        ):
            add_ships(
                empire,
                ship_class=ship_class,
                template=template,
                rng=rng,
                engine=engine,
            )


def get_fleets_by_empire_id(engine: Engine, *, empire_id: int):
    return pd.read_sql(
        select(Fleet.fleet_id).where(Fleet.fleet_empire_owner == empire_id),
        engine,
    )


def get_templates_by_class_type(engine: Engine, *, ship_class: str):
    return pd.read_sql(
        select(ShipTemplate.ship_template_id, ShipTemplate.ship_template_name)
        .join(ShipClass)
        .where(ShipClass.ship_class_name == ship_class),
        engine,
    )


def add_ships(
    empire: pd.Series,
    *,
    ship_class: str,
    template: int,
    rng: np.random.Generator,
    engine: Engine,
):
    num_ships = empire[f"num_{ship_class}"]

    if num_ships <= 0:
        return

    ship_suffix_file = "./assets/ship_suffix.txt"

    with get_session(engine) as session:
        session.execute(
            insert(Spaceship).values(
                [
                    {
                        "spaceship_name": f"{empire['empire_ship_prefix']} "
                        f"{suffix}",
                        "spaceship_fleet_id": int(fleet),
                        "spaceship_template_id": int(template),
                        "spaceship_experience": int(xp),
                    }
                    for fleet, suffix, xp in zip(
                        rng.choice(
                            get_fleets_by_empire_id(
                                engine, empire_id=int(empire["empire_id"])
                            )["fleet_id"],
                            size=num_ships,
                            replace=True,
                        ),
                        rng.choice(
                            load_file(get_location(), ship_suffix_file),
                            size=num_ships,
                            replace=True,
                        ),
                        rng.integers(
                            0, empire["command_limit"] + 1, size=num_ships
                        ),
                    )
                ]
            )
        )
