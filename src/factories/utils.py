from faker.providers import BaseProvider

STARTING_ID = 1


class IntegerOrNone(BaseProvider):
    def integer_or_none(self, min_value=0, max_value=100, null_chance=0.5):
        if self.generator.random.random() < null_chance:
            return None
        else:
            return self.random_int(min=min_value, max=max_value)
