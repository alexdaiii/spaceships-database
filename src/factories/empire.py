import os
from functools import lru_cache

import factory
from factory import fuzzy
from faker import Faker


from src.factories.utils import (
    STARTING_ID,
    IntegerOrNone,
)
from src.models import EmpireAuthority, EmpireEthic, Empire, EmpireToEthic
from src.settings import Settings

settings = Settings()

factory.Faker.add_provider(IntegerOrNone)

_stellaris_authorities = [
    "oligarchic",
    "democratic",
    "dictatorial",
    "imperial",
    "hive_mind",
    "machine_intelligence",
]


class EmpireAuthorityFactory(factory.Factory):
    class Meta:
        model = EmpireAuthority

    empire_authority_id = factory.Sequence(lambda n: n)
    empire_authority_name = factory.Sequence(
        lambda n: _stellaris_authorities[n % len(_stellaris_authorities)]
    )


def create_empire_authorities():
    EmpireAuthorityFactory.reset_sequence(STARTING_ID)
    return EmpireAuthorityFactory.create_batch(len(_stellaris_authorities))


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


class EmpireEthicFactory(factory.Factory):
    class Meta:
        model = EmpireEthic

    empire_ethic_id = factory.Sequence(lambda n: n)
    empire_ethic_name = factory.Sequence(
        lambda n: _stellaris_ethics[n % len(_stellaris_ethics)]
    )


def create_empire_ethics():
    EmpireEthicFactory.reset_sequence(STARTING_ID)
    return EmpireEthicFactory.create_batch(len(_stellaris_ethics))


@lru_cache()
def empire_suffix():
    location = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )

    suffix_file = os.path.join(location, "empire_suffix.txt")
    print(f"Loading suffixes from {suffix_file}")
    with open(suffix_file) as f:
        suffixes = f.read().splitlines()
    return suffixes


@lru_cache()
def empire_species():
    location = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )

    species_file = os.path.join(location, "empire_species.txt")
    print(f"Loading species from {species_file}")
    with open(species_file) as f:
        species = f.read().splitlines()
    return species


def get_empire_name(n: int):
    suffix_idx = fuzzy.FuzzyInteger(0, len(empire_suffix()) - 1).fuzz()

    return f"{empire_species()[n % len(empire_species())]} {empire_suffix()[suffix_idx]}"


class EmpireFactory(factory.Factory):
    class Meta:
        model = Empire

    class Params:
        get_empire_name = lambda x: factory.Faker("get_empire_name", n=x)

    empire_id = factory.Sequence(lambda n: n)
    empire_authority_id = fuzzy.FuzzyInteger(
        STARTING_ID, len(_stellaris_authorities)
    )
    empire_name = factory.Sequence(lambda n: get_empire_name(n))
    empire_score = factory.Faker("integer_or_none", null_chance=0.1)


def create_empires():
    EmpireFactory.reset_sequence(STARTING_ID)
    return EmpireFactory.create_batch(settings.number_of_empires)


MIN_NUM_ETHICS = 2
MAX_NUM_ETHICS = 3


def create_empire_to_ethic(fake: Faker):
    empire_ethics = []
    for i in range(1, settings.number_of_empires + 1):
        num_ethics = fake.random_int(MIN_NUM_ETHICS, MAX_NUM_ETHICS)
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
                    empire_ethic_id=empire_ethic_list[j],
                    empire_ethic_attraction=attraction_list[j],
                )
                for j in range(num_ethics)
            ]
        )

    return empire_ethics


__all__ = [
    "create_empire_authorities",
    "create_empire_ethics",
    "create_empires",
    "create_empire_to_ethic",
]
