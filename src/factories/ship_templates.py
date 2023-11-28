import math
from collections import Counter
from functools import lru_cache

import colorful as cf
import numpy as np
import pandas as pd
from faker import Faker
from sqlalchemy import Engine, insert

from src.database.db import get_session
from src.models import (
    ShipClass,
    SpaceshipModule,
    ShipTemplate,
    ShipTemplateModule,
)
from src.util import df_info

from .utils.ships_util import ship_class_df, ship_modules
from .utils.util import STARTING_ID


@lru_cache()
def ship_templates_df(fake: Faker):
    exponent = 1.5

    ship_companies = [
        fake.company()
        for _ in range(math.ceil((len(ship_class_df()) + 1) ** exponent))
    ]

    templates = []

    for i, (_, ship_class) in enumerate(
        (
            ship_class_df()
            .sort_values("ship_command_points", ascending=False)
            .iterrows()
        ),
        start=1,
    ):
        num_templates = int(i**exponent)

        # convert snake case to spaces and capitalize first letter of each word
        ship_class_name = (
            ship_class["ship_class_name"].replace("_", " ").title()
        )

        print(f"Creating {num_templates} ship templates for {ship_class_name}")

        templates.extend(
            [
                {
                    "ship_template_name": f"{ship_company} {ship_class_name}",
                    "ship_class_id": ship_class.name,
                }
                for ship_company in fake.random_elements(
                    ship_companies, length=num_templates, unique=True
                )
            ]
        )

    df = pd.DataFrame(templates)
    df["ship_template_id"] = df.index + STARTING_ID
    return df.set_index("ship_template_id")


def add_ship_templates(
    *, rng: np.random.Generator, fake: Faker, engine: Engine
):
    add_ship_classes(engine)
    add_ship_mods(engine)
    insert_ship_templates(engine, fake)
    add_ship_template_mods(engine, fake)


def insert_ship_templates(engine: Engine, fake: Faker):
    print(cf.yellow("Adding ship templates"))

    with get_session(engine) as session:
        session.execute(
            insert(ShipTemplate),
            ship_templates_df(fake).reset_index().to_dict("records"),
        )


def add_ship_classes(engine: Engine):
    print(cf.yellow("Adding ship classes"))

    with get_session(engine) as session:
        session.execute(
            insert(ShipClass), ship_class_df().reset_index().to_dict("records")
        )


def add_ship_mods(engine: Engine):
    print(cf.yellow("Adding ship modules"))

    with get_session(engine) as session:
        session.execute(
            insert(SpaceshipModule),
            ship_modules().reset_index().to_dict("records"),
        )


def add_ship_template_mods(engine: Engine, fake: Faker):
    print(cf.yellow("Adding ship template modules"))

    template_modules = []

    for _, template in ship_templates_df(fake).iterrows():
        ship_class = ship_class_df().loc[template["ship_class_id"]]
        for ship_module_size in ship_modules().spaceship_module_size.unique():
            num_slots = ship_class[f"{ship_module_size}_component_slots"]

            if num_slots == 0:
                continue

            template_modules.extend(
                extend_template_mods(
                    num_slots=num_slots,
                    fake=fake,
                    size=ship_module_size,
                    template_id=int(template.name),
                )
            )

    with get_session(engine) as session:
        session.execute(
            insert(ShipTemplateModule),
            template_modules,
        )


def extend_template_mods(
    *, num_slots: int, size: str, fake: Faker, template_id: int
):
    # use python counter
    return [
        {
            "ship_template_id": template_id,
            "ship_module_id": component_id,
            "ship_module_count": count,
        }
        for component_id, count in Counter(
            # create a random list of modules for the ship template
            fake.random_elements(
                ship_modules()[
                    ship_modules().spaceship_module_size == size
                ].index.tolist(),
                length=num_slots,
            )
        ).items()
    ]


__all__ = ["add_ship_templates"]
