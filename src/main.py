import colorful as cf
import factory.random
import numpy as np
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src import factories
from src.database.base import Base
from src.database.db import get_session
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

        factories.create_stars(
            fake=fake,
            rng=rng,
            engine=engine,
            num_stars=settings.num_stars,
        )
        factories.create_planets(
            rng=rng,
            engine=engine,
        )
        # with get_session(engine) as session:
        #     fake, rng = reset_random_seed(settings.random_seed)
        #
        #     fleets = factories.create_fleets(
        #         fake,
        #         max_num_fleets=settings.empire_max_fleets,
        #         num_empires=settings.number_of_empires,
        #     )
        #
        #     inserts = [
        #         *factories.create_empire_authorities(),
        #         *factories.create_empire_ethics(),
        #         *factories.create_empires(
        #             fake,
        #             num_empires=settings.number_of_empires,
        #             null_chance=0.1,
        #         ),
        #         *factories.create_empire_to_ethic(
        #             fake, num_empires=settings.number_of_empires
        #         ),
        #         *fleets,
        #         *factories.create_ships(
        #             fake,
        #             rng=rng,
        #             num_fleets=len(fleets),
        #             max_ships=settings.max_ships_per_fleet,
        #         ),
        #     ]
        #
        #     session.add_all(inserts)
        #     session.commit()


if __name__ == "__main__":
    s = get_settings()
    main(settings=s)
