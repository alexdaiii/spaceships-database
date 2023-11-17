from enum import Enum

from pydantic_settings import BaseSettings
from pydantic import MySQLDsn, computed_field, PostgresDsn, MariaDBDsn, Field


class TargetDatabase(Enum):
    """
    This is an enum that represents the target database

    Available options are:
    - MYSQL
    - POSTGRESQL
    - MARIADB
    - SQLITE
    """

    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    MARIADB = "mariadb"
    SQLITE = "sqlite"


class Settings(BaseSettings):
    # MySQL
    mysql_host: str = "localhost"
    mysql_root_user: str = "root"
    mysql_root_password: str = "root"
    mysql_database: str = "spaceships"
    mysql_port: int = 3306

    @computed_field
    @property
    def mysql_dsn(self) -> MySQLDsn:
        return MySQLDsn.build(
            scheme="mysql+pymysql",
            username=self.mysql_root_user,
            password=self.mysql_root_password,
            host=self.mysql_host,
            port=self.mysql_port,
            path=self.mysql_database,
        )

    # PostgreSQL
    postgresql_host: str = "localhost"
    postgresql_username: str = "postgres"
    postgresql_password: str = "postgres"
    postgresql_database: str = "spaceships"
    postgresql_port: int = 5432

    @computed_field
    @property
    def postgresql_dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.postgresql_username,
            password=self.postgresql_password,
            host=self.postgresql_host,
            port=self.postgresql_port,
            path=self.postgresql_database,
        )

    # MariaDB
    mariadb_host: str = "localhost"
    mariadb_root_user: str = "root"
    mariadb_root_password: str = "root"
    mariadb_database: str = "spaceships"
    mariadb_port: int = 3306

    @computed_field
    @property
    def mariadb_dsn(self) -> MariaDBDsn:
        return MariaDBDsn.build(
            scheme="mariadb+pymysql",
            username=self.mariadb_root_user,
            password=self.mariadb_root_password,
            host=self.mariadb_host,
            port=self.mariadb_port,
            path=self.mariadb_database,
        )

    # Sqlite
    sqlite_database: str = "../data/sqlite.db"

    # sqlalchemy
    target_databases: list[TargetDatabase] = []
    sqlalchemy_echo: bool = False

    # config
    random_seed: int = 1234
    number_of_empires: int = Field(100, min=1, max=100)
    empire_max_fleets: int = Field(10, min=0, max=20)
    max_ships_per_fleet: int = Field(100, min=1, max=1000)

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
