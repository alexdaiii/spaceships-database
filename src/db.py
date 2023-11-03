from sqlalchemy.orm import Session, sessionmaker
from contextlib import contextmanager
from sqlalchemy import text, create_engine

engine = create_engine(settings2.SQL_DB, connect_args={"check_same_thread": False})
# a sessionmaker(), also in the same scope as the engine
Session = sessionmaker(engine)


@contextmanager
def get_session() -> Session:
    with Session.begin() as session:
        try:
            # issue command to enable type checking
            session.execute(text("PRAGMA foreign_keys=ON;"))

            yield session
        except:
            print("An error occurred, rolling back")
            session.rollback()
            raise


@contextmanager
def mock_session() -> Session:
    """
    This is a mock session that will rollback instead of commit
    """

    with Session.begin() as session:
        try:
            yield session
        except:
            print("An error occurred, rolling back")
            session.rollback()
            raise
        finally:
            print("Success, rolling back. (NOTE: This is a mock session)")
            session.rollback()
