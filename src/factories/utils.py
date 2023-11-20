import os
from functools import lru_cache

from faker.providers import BaseProvider

STARTING_ID = 1


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
