import math
import os
from enum import Enum
from functools import lru_cache

import colorful as cf
from pydantic import Field, MariaDBDsn, MySQLDsn, PostgresDsn, computed_field
from pydantic_settings import BaseSettings

from src.util import (MAX_NUM_STARS, MIN_NUM_STARS, get_location, get_m_and_b,
                      get_yhat)


@lru_cache()
def get_num_empires(num_stars: int) -> int:
    base_min_empires = {
        "stars": 200,
        "empires": 6,
    }
    base_max_empires = {
        "stars": 1000,
        "empires": 30,
    }
    max_num_empires = 300

    return min(
        math.ceil(
            get_yhat(
                num_stars,
                *get_m_and_b(
                    base_min_empires["stars"],
                    base_min_empires["empires"],
                    base_max_empires["stars"],
                    base_max_empires["empires"],
                ),
            )
        ),
        max_num_empires,
    )


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
    sqlite_database: str = "sqlite.db"

    @computed_field
    @property
    def sqlite_dsn(self) -> str:
        location = get_location()

        data_dir = os.path.join(location, "../data")

        if not os.path.exists(data_dir):
            os.mkdir(data_dir)

        return f"sqlite:///{os.path.join(data_dir, self.sqlite_database)}"

    # sqlalchemy
    target_databases: list[TargetDatabase] = []
    sqlalchemy_echo: bool = True

    # config
    random_seed: int = 1234
    num_stars: int = Field(MIN_NUM_STARS, ge=MIN_NUM_STARS, le=MAX_NUM_STARS)
    hyperlane_density: float = Field(0.5, ge=0.5, le=2.5)

    @computed_field
    @property
    def number_of_empires(self) -> int:
        return get_num_empires(self.num_stars)

    class Config:
        env_file = os.path.join(get_location(), "../.env")
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    print(cf.yellow("Loading settings..."))
    return Settings()
