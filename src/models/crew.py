import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class Crew(Base):
    __tablename__ = "crew"

    crew_id: Mapped[int] = mapped_column(primary_key=True)
    crew_name: Mapped[str] = mapped_column(String(255))
    spaceship_id: Mapped[int] = mapped_column(
        ForeignKey("spaceship.spaceship_id"),
    )
    command_points: Mapped[int] = mapped_column(default=0)
    reports_to: Mapped[int | None] = mapped_column(
        ForeignKey("crew.crew_id"), nullable=True
    )
    birth_date: Mapped[datetime.datetime]
    hire_date: Mapped[datetime.datetime]
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
