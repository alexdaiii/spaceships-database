from contextlib import contextmanager
from typing import Literal

import colorful as cf
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker


class HashableEngine:
    def __init__(self, engine: Engine):
        self.engine = engine

    def __hash__(self):
        # returns the has of the dsn
        return hash(self.engine.url.__str__())


def _issue_callback(
    session: Session,
    fn: (lambda session: Session) = None,
):
    if fn is not None:
        fn(session)


@contextmanager
def _make_session(
    engine: Engine,
    *,
    setup_callback: (lambda session: Session) = None,
    teardown_callback: (lambda session: Session) = None,
) -> Session:
    """
    This is a context manager that will automatically commit or rollback
    """
    with Session(engine) as session:
        try:
            # issue command to enable type checking
            _issue_callback(session, setup_callback)

            yield session
        except Exception as e:
            # cannot use 3.12 f strings bc of black error with mypy
            print(f"{cf.bold_red('An error occurred, rolling back')}")
            raise
        finally:
            _issue_callback(session, teardown_callback)
            session.commit()


def _sqlite_setup_callback(session: Session):
    session.execute(text("PRAGMA foreign_keys=ON"))


@contextmanager
def get_session(engine: Engine):
    if engine.dialect.name == "sqlite":
        with _make_session(
            engine, setup_callback=_sqlite_setup_callback
        ) as session:
            yield session
    elif (
        engine.dialect.name == "mysql"
        or engine.dialect.name == "mariadb"
        or engine.dialect.name == "postgresql"
    ):
        with _make_session(engine) as session:
            yield session

    else:
        raise NotImplementedError("Database not supported")
