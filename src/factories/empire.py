import colorful as cf
import numpy as np
from faker import Faker
from sqlalchemy import Engine, insert

from src.database.db import get_session
from src.models import Empire, EmpireAuthority, EmpireEthic, EmpireToEthic
from src.util import get_location

from .empires_util import authority_df, empire_id_range, ethic_df
from .utils import load_file


def create_empire_authorities(engine: Engine):
    print(cf.yellow("Adding empire authorities..."))
    with get_session(engine) as session:
        session.execute(
            insert(EmpireAuthority),
            authority_df().reset_index().to_dict("records"),
        )


def create_empire_ethics(engine: Engine):
    print(cf.yellow("Adding empire ethics..."))
    with get_session(engine) as session:
        session.execute(
            insert(EmpireEthic),
            ethic_df().reset_index().to_dict("records"),
        )


def create_empires(
    fake: Faker, *, rng: np.random.Generator, num_empires: int, engine: Engine
):
    create_empire_authorities(engine)
    create_empire_ethics(engine)

    create_empires_helper(
        fake=fake,
        num_empires=num_empires,
        engine=engine,
    )

    create_empire_to_ethic(
        rng=rng,
        engine=engine,
    )


def create_empires_helper(
    fake: Faker,
    *,
    num_empires: int,
    engine: Engine,
):
    empire_species_file = "assets/empire_species.txt"
    empire_suffix_file = "assets/empire_suffix.txt"

    location = get_location()

    print(cf.yellow("Adding empires..."))

    with get_session(engine) as session:
        session.execute(
            insert(Empire),
            [
                {
                    "empire_name": f"{species} {suffix}",
                    "empire_authority_id": auth_id,
                }
                for auth_id, species, suffix in zip(
                    fake.random_elements(
                        elements=authority_df().index,
                        length=num_empires,
                    ),
                    fake.random_elements(
                        elements=load_file(location, empire_species_file),
                        length=num_empires,
                        unique=True,
                    ),
                    fake.random_elements(
                        elements=load_file(location, empire_suffix_file),
                        length=num_empires,
                    ),
                )
            ],
        )


def generate_empire_ethics(rng: np.random.Generator, *, engine: Engine):
    min_num_ethics = 2
    max_num_ethics = 3
    base_ethic_attraction = 1
    fanatic_ethic_attraction = 2

    print(cf.yellow("Adding empire to ethic..."))

    min_id, max_id = empire_id_range(engine)

    empire_ethics = []
    for num_ethics, empire_id in zip(
        rng.integers(
            low=min_num_ethics,
            high=max_num_ethics + 1,
            size=max_id - min_id + 1,
        ),
        range(min_id, max_id + 1),
    ):
        new_ethics = [
            {
                "empire_id": empire_id,
                "empire_ethic_id": int(ethic_id),
                "empire_ethic_attraction": base_ethic_attraction,
            }
            for ethic_id in rng.choice(
                ethic_df().index,
                size=num_ethics,
                replace=False,
            )
        ]

        if num_ethics == min_num_ethics:
            # choose a random ethic and make it fanatic
            fanatic_ethic = rng.choice([i for i in range(len(new_ethics))])
            new_ethics[fanatic_ethic][
                "empire_ethic_attraction"
            ] = fanatic_ethic_attraction

        empire_ethics.extend(new_ethics)

    return empire_ethics


def create_empire_to_ethic(rng: np.random.Generator, *, engine: Engine):
    empire_ethics = generate_empire_ethics(rng, engine=engine)

    with get_session(engine) as session:
        session.execute(
            insert(EmpireToEthic),
            empire_ethics,
        )


__all__ = [
    "create_empires",
]
