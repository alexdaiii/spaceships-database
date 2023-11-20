import colorful as cf
import numpy as np
from faker import Faker
from sqlalchemy import Engine


def create_planets(
        *,
        fake: Faker,
        rng: np.random.Generator,
        engine: Engine,
):
    print(cf.yellow("Generating planets..."))
