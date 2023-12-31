import colorful as cf
from sqlalchemy import Engine, insert

from src.database.db import get_session
from src.models import SpaceshipRank

from .utils.ships_util import ships_info


def add_ship_ranks(engine: Engine):
    print(cf.yellow("Adding ship ranks..."))

    with get_session(engine) as session:
        session.execute(
            insert(SpaceshipRank),
            ships_info().model_dump(include=["ranks"])["ranks"],
        )


__all__ = ["add_ship_ranks"]
