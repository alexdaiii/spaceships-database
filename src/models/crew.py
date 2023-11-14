import datetime

from src.database.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.ship import Spaceship
    from src.models.star_system import Planet


class Crew(Base):
    __tablename__ = "crew"

    crew_id: Mapped[int] = mapped_column(primary_key=True)
    crew_name: Mapped[str] = mapped_column()
    spaceship_id: Mapped[int] = mapped_column(
        ForeignKey("spaceship.spaceship_id")
    )
    base_command_points: Mapped[int] = mapped_column()
    reports_to: Mapped[int] = mapped_column(ForeignKey("crew.crew_id"))
    birth_date: Mapped[datetime.datetime] = mapped_column()
    hire_date: Mapped[datetime.datetime] = mapped_column()
    planet_of_birth_id: Mapped[int] = mapped_column(
        ForeignKey("planet.planet_id")
    )

    spaceship: Mapped["Spaceship"] = relationship(
        "Spaceship",
        back_populates="crew",
    )
    reports_to_crew: Mapped["Crew"] = relationship(
        "Crew",
        back_populates="managed_crew",
    )
    managed_crew: Mapped[list["Crew"]] = relationship(
        "Crew",
        back_populates="reports_to_crew",
    )
    planet_of_birth: Mapped["Planet"] = relationship(
        "Planet",
        back_populates="crew",
    )
    friends: Mapped[list["Crew"]] = relationship(
        "Crew",
        secondary="crew_friend",
        primaryjoin="Crew.crew_id==CrewFriend.crew_id",
        secondaryjoin="Crew.crew_id==CrewFriend.friend_id",
        back_populates="friends",
    )


class CrewFriend(Base):
    __tablename__ = "crew_friend"

    crew_id: Mapped[int] = mapped_column(
        ForeignKey("crew.crew_id"), primary_key=True
    )
    friend_id: Mapped[int] = mapped_column(
        ForeignKey("crew.crew_id"), primary_key=True
    )
