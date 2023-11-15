import inspect

from src.database.base import Base
from src.settings import Settings, TargetDatabase
from src import models as mods

from sqlalchemy import create_engine


def get_dsn(settings: Settings, database: TargetDatabase):
    if database == TargetDatabase.SQLITE:
        return f"sqlite:///{settings.sqlite_database}"
    elif database == TargetDatabase.MYSQL:
        return settings.mysql_dsn
    elif database == TargetDatabase.MARIADB:
        return settings.mariadb_dsn
    elif database == TargetDatabase.POSTGRESQL:
        return settings.postgresql_dsn
    else:
        raise ValueError("Unimplemented database type")


def main():
    settings = Settings()

    models = [
        m
        for m in mods.__dict__.values()
        if inspect.isclass(m) and issubclass(m, Base)
    ]

    for database in settings.target_databases:
        engine = create_engine(get_dsn(settings, database), echo=True)

        print(f"Adding models to {database.value} database")

        Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()
