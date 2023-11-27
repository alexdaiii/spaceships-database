import colorful as cf
import numpy as np
from faker import Faker
from sqlalchemy import create_engine

from src.database.base import Base
from src.factories import generate_galaxy
from src.settings import Settings, TargetDatabase, get_settings


def get_dsn(settings: Settings, database: TargetDatabase):
    def _get_dsn():
        if database == TargetDatabase.SQLITE:
            return settings.sqlite_dsn
        elif database == TargetDatabase.MYSQL:
            return settings.mysql_dsn
        elif database == TargetDatabase.MARIADB:
            return settings.mariadb_dsn
        elif database == TargetDatabase.POSTGRESQL:
            return settings.postgresql_dsn
        else:
            raise NotImplementedError("Database not supported")

    return _get_dsn().__str__()


def reset_random_seed(seed: int):
    fake = Faker()
    Faker.seed(seed)

    rng = np.random.default_rng(seed)

    return fake, rng


def main(settings: Settings):
    cf.use_true_colors()

    for database in settings.target_databases:
        fake, rng = reset_random_seed(settings.random_seed)

        engine = create_engine(
            get_dsn(settings, database), echo=settings.sqlalchemy_echo
        )

        db_name = cf.bold_cyan(database.value.upper())

        print(f"DROPPING ALL TABLES IN {db_name} DATABASE")
        Base.metadata.drop_all(engine)

        print(f"Adding models to {db_name} database")

        Base.metadata.create_all(engine)

        print(f"Adding data to {db_name} database")

        generate_galaxy(
            fake=fake,
            rng=rng,
            engine=engine,
            settings=settings,
        )


if __name__ == "__main__":
    s = get_settings()
    main(settings=s)
