from typing import Literal

from sqlalchemy.orm import Session, sessionmaker
from contextlib import contextmanager
from sqlalchemy import Engine, text


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

    session_maker = sessionmaker(bind=engine)

    with session_maker.begin() as session:
        try:
            # issue command to enable type checking
            _issue_callback(session, setup_callback)

            yield session
        except Exception as e:
            print("An error occurred, rolling back")
            print(e)
            session.rollback()
            raise
        finally:
            _issue_callback(session, teardown_callback)


@contextmanager
def _mock_session(
    engine: Engine,
    *,
    setup_callback: (lambda session: Session) = None,
) -> Session:
    """
    This is a mock session that will rollback instead of commit
    """

    def teardown_callback(sess: Session):
        sess.rollback()

    with _make_session(
        engine,
        setup_callback=setup_callback,
        teardown_callback=teardown_callback,
    ) as session:
        yield session


def _sqlite_setup_callback(session: Session):
    session.execute(text("PRAGMA foreign_keys=ON"))


def _get_maker_fn(sess_type: Literal["mock", "real"]):
    if sess_type == "mock":
        return _mock_session
    elif sess_type == "real":
        return _make_session
    else:
        raise NotImplementedError("Database not supported")


@contextmanager
def get_session(
    engine: Engine,
    sess_type: Literal["mock", "real"] = "real",
):
    maker_fn = _get_maker_fn(sess_type)

    if engine.dialect.name == "sqlite":
        with maker_fn(
            engine, setup_callback=_sqlite_setup_callback
        ) as session:
            yield session
    elif (
        engine.dialect.name == "mysql"
        or engine.dialect.name == "mariadb"
        or engine.dialect.name == "postgresql"
    ):
        with maker_fn(engine) as session:
            yield session
    else:
        raise NotImplementedError("Database not supported")
