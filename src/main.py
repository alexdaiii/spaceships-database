from src.database.base import Base
from src.database.db import get_session
from src.settings import Settings, TargetDatabase
from src import models
from src import factories
import colorful as cf
import factory.random


from sqlalchemy import create_engine

settings = Settings()


def get_dsn(database: TargetDatabase):
    def _get_dsn():
        if database == TargetDatabase.SQLITE:
            return f"sqlite:///{settings.sqlite_database}"
        elif database == TargetDatabase.MYSQL:
            return settings.mysql_dsn
        elif database == TargetDatabase.MARIADB:
            return settings.mariadb_dsn
        elif database == TargetDatabase.POSTGRESQL:
            return settings.postgresql_dsn
        else:
            raise NotImplementedError("Database not supported")

    return _get_dsn().__str__()


def reset_random_seed():
    factory.random.reseed_random(settings.random_seed)


def main():
    cf.use_true_colors()

    for database in settings.target_databases:
        engine = create_engine(get_dsn(database), echo=False)

        db_name = cf.bold_cyan(database.value.upper())

        print(f"DROPPING ALL TABLES IN {db_name} DATABASE")
        Base.metadata.drop_all(engine)

        print(f"Adding models to {db_name} database")

        Base.metadata.create_all(engine)

        with get_session(engine, sess_type="mock") as session:
            reset_random_seed()

            inserts = [
                *factories.create_empire_authorities(),
                *factories.create_empire_ethics(),
                *factories.create_empires(),
                *factories.create_empire_to_ethic(settings.random_seed),
            ]

            session.add_all(inserts)
            session.commit()


if __name__ == "__main__":
    main()
