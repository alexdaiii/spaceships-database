from sqlalchemy import Engine, insert

from src.database.db import get_session
from src.factories.utils.ships_util import ships_info
from src.models import SpaceshipRank


def add_ship_ranks(engine: Engine):
    with get_session(engine) as session:
        session.execute(
            insert(SpaceshipRank),
            ships_info().model_dump(include=["ranks"])["ranks"],
        )


__all__ = ["add_ship_ranks"]
