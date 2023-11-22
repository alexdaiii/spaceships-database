import os
from functools import lru_cache

from faker.providers import BaseProvider

STARTING_ID = 1
MIN_PLANET_SIZE = 2
MAX_PLANET_SIZE = 25


@lru_cache()
def load_file(location: str, filename: str):
    filepath = os.path.join(location, filename)
    print(f"Loading {filename} from {filepath}")
    with open(filepath, "r") as f:
        data = f.read().splitlines()

    return data


class IntegerOrNone(BaseProvider):
    def integer_or_none(self, min_value=0, max_value=100, null_chance=0.5):
        if self.generator.random.random() < null_chance:
            return None
        else:
            return self.random_int(min=min_value, max=max_value)


def get_m_and_b(
    x1: float, y1: float, x2: float, y2: float
) -> tuple[float, float]:
    """
    Get the slope and y-intercept of a line given two points.
    """
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1
    return m, b


def get_yhat(x: float, m: float, b: float) -> float:
    """
    Get the y-value of a line given an x-value, slope, and y-intercept.
    """
    return m * x + b
