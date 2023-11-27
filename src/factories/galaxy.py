import numpy as np
from faker import Faker
from sqlalchemy import Engine

from src.settings import Settings

from .empire import create_empires
from .empire_star_systems import assign_empire_star_systems
from .planet_resources import add_planet_pops
from .planets import create_planets
from .stars import create_stars


def generate_galaxy(
    fake: Faker,
    rng: np.random.Generator,
    engine: Engine,
    settings: Settings,
):
    create_stars(
        fake=fake,
        rng=rng,
        engine=engine,
        num_stars=settings.num_stars,
    )
    create_planets(
        rng=rng,
        engine=engine,
    )
    create_empires(
        fake=fake,
        rng=rng,
        num_empires=settings.number_of_empires,
        engine=engine,
    )
    assign_empire_star_systems(
        rng=rng,
        engine=engine,
        num_empires=settings.number_of_empires,
        num_stars=settings.num_stars,
    )
    add_planet_pops(
        rng=rng,
        engine=engine,
    )


__all__ = ["generate_galaxy"]
