import datetime

from src.database.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class Crew(Base):
    __tablename__ = "crew"

    crew_id: Mapped[int] = mapped_column(primary_key=True)
    crew_name: Mapped[str]
    spaceship_id: Mapped[int | None] = mapped_column(
        ForeignKey("spaceship.spaceship_id"),
        nullable=True,
    )
    command_points: Mapped[int | None]
    reports_to: Mapped[int | None] = mapped_column(
        ForeignKey("crew.crew_id"), nullable=True
    )
    birth_date: Mapped[datetime.datetime]
    hire_date: Mapped[datetime.datetime | None]
    planet_of_birth_id: Mapped[int] = mapped_column(
        ForeignKey("planet.planet_id")
    )


class CrewFriend(Base):
    __tablename__ = "crew_friend"

    crew_id: Mapped[int] = mapped_column(
        ForeignKey("crew.crew_id"), primary_key=True
    )
    friend_id: Mapped[int] = mapped_column(
        ForeignKey("crew.crew_id"), primary_key=True
    )


__all__ = [
    "Crew",
    "CrewFriend",
]
