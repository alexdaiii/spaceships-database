from enum import Enum

from pydantic_settings import BaseSettings
from pydantic import MySQLDsn, computed_field, PostgresDsn, MariaDBDsn


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
    mysql_database: str = "mysql"
    mysql_port: int = 3306

    @computed_field
    @property
    def mysql_dsn(self) -> MySQLDsn:
        return MySQLDsn.build(
            scheme="mysql",
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
    postgresql_database: str = "postgres"
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
    mariadb_database: str = "mariadb"
    mariadb_port: int = 3306

    @computed_field
    @property
    def mariadb_dsn(self) -> MariaDBDsn:
        return MariaDBDsn.build(
            scheme="mariadb",
            username=self.mariadb_root_user,
            password=self.mariadb_root_password,
            host=self.mariadb_host,
            port=self.mariadb_port,
            path=self.mariadb_database,
        )

    # Sqlite
    sqlite_database: str = "sqlite.db"

    target_databases: list[TargetDatabase] = []

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
