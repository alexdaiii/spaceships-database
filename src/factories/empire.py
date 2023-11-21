from faker import Faker

from src.models import Empire, EmpireAuthority, EmpireEthic, EmpireToEthic
from src.util import get_location

from .utils import STARTING_ID, IntegerOrNone, load_file

_stellaris_authorities = [
    "oligarchic",
    "democratic",
    "dictatorial",
    "imperial",
    "hive_mind",
    "machine_intelligence",
]


def create_empire_authorities():
    return [
        EmpireAuthority(
            empire_authority_id=i,
            empire_authority_name=_stellaris_authorities[
                i % len(_stellaris_authorities)
            ],
        )
        for i in range(STARTING_ID, len(_stellaris_authorities) + 1)
    ]


_stellaris_ethics = [
    "egalitarian",
    "authoritarian",
    "xenophobe",
    "xenophile",
    "pacifist",
    "militarist",
    "materialist",
    "spiritualist",
]


def create_empire_ethics():
    return [
        EmpireEthic(
            empire_ethic_id=i,
            empire_ethic_name=_stellaris_ethics[i % len(_stellaris_ethics)],
        )
        for i in range(STARTING_ID, len(_stellaris_ethics) + 1)
    ]


def create_empires(fake: Faker, *, num_empires: int, null_chance: float):
    fake.add_provider(IntegerOrNone)

    empire_species_file = "assets/empire_species.txt"
    empire_suffix_file = "assets/empire_suffix.txt"

    location = get_location()

    return [
        Empire(
            empire_id=i,
            empire_authority_id=fake.random_int(
                min=STARTING_ID, max=len(_stellaris_authorities)
            ),
            empire_name=(
                f"{species} "
                f"{fake.random_element(load_file(location=location, filename=empire_suffix_file, ))}"
            ),
            empire_score=fake.integer_or_none(null_chance=null_chance),
        )
        for i, species in enumerate(
            fake.random_elements(
                elements=load_file(
                    location=location,
                    filename=empire_species_file,
                ),
                length=num_empires,
                unique=True,
            ),
            start=STARTING_ID,
        )
    ]


def create_empire_to_ethic(fake: Faker, *, num_empires: int):
    min_num_ethics = 2
    max_num_ethics = 3

    empire_ethics = []
    for i in range(STARTING_ID, num_empires + 1):
        num_ethics = fake.random_int(min_num_ethics, max_num_ethics)
        empire_ethic_list = fake.random_elements(
            elements=range(1, len(_stellaris_ethics)),
            length=num_ethics,
            unique=True,
        )
        attraction_list = [fake.random_int(0, 100) for _ in range(num_ethics)]

        empire_ethics.extend(
            [
                EmpireToEthic(
                    empire_id=i,
                    empire_ethic_id=ethic_id,
                    empire_ethic_attraction=attraction_id,
                )
                for j, (ethic_id, attraction_id) in enumerate(
                    zip(empire_ethic_list, attraction_list)
                )
            ]
        )

    return empire_ethics


__all__ = [
    "create_empire_authorities",
    "create_empire_ethics",
    "create_empires",
    "create_empire_to_ethic",
]
