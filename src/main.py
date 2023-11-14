from src.settings import Settings, TargetDatabase

from sqlalchemy import create_engine


def get_dsn(settings: Settings, database: TargetDatabase):
    if database == TargetDatabase.SQLITE:
        return f"sqlite://{settings.sqlite_path}"
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

    for database in settings.target_databases:
        engine = create_engine(get_dsn(settings, database), echo=True)


if __name__ == "__main__":
    main()
