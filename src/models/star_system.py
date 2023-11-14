"""
CREATE TABLE star_system (
    star_system_id INTEGER PRIMARY KEY,
    star_system_name VARCHAR NOT NULL,
    system_trade_value INTEGER NOT NULL,
    system_energy_value INTEGER NOT NULL,
    system_minerals_value INTEGER NOT NULL,
    system_research_value INTEGER NOT NULL,
    empire_owner INTEGER NOT NULL,

    FOREIGN KEY (empire_owner) REFERENCES empire (empire_id)
);

CREATE TABLE patrolled_systems (
    star_system_id INTEGER NOT NULL,
    fleet_id INTEGER NOT NULL,
    last_patrol_date DATE NOT NULL,

    FOREIGN KEY (star_system_id) REFERENCES star_system (star_system_id),
    FOREIGN KEY (fleet_id) REFERENCES fleet (fleet_id),
    PRIMARY KEY (star_system_id, fleet_id)
);

CREATE TABLE planet_biome (
    biome_id INTEGER PRIMARY KEY,
    biome_name VARCHAR NOT NULL
);

CREATE TABLE planet (
    planet_id INTEGER PRIMARY KEY,
    planet_name VARCHAR NOT NULL,
    planet_size INTEGER NOT NULL,
    star_system_id INTEGER NOT NULL,
    biome_id INTEGER NOT NULL,

    FOREIGN KEY (star_system_id) REFERENCES star_system (star_system_id)
);
"""
import datetime

from src.database.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.fleet import Fleet
    from src.models.empire import Empire


class StarSystem(Base):
    __tablename__ = "star_system"

    star_system_id: Mapped[int] = mapped_column(primary_key=True)
    star_system_name: Mapped[str] = mapped_column()
    system_trade_value: Mapped[int] = mapped_column()
    system_energy_value: Mapped[int] = mapped_column()
    system_minerals_value: Mapped[int] = mapped_column()
    system_research_value: Mapped[int] = mapped_column()
    empire_owner: Mapped[int] = mapped_column(ForeignKey("empire.empire_id"))

    empire: Mapped["Empire"] = relationship(
        "Empire",
        back_populates="star_systems",
    )
    patrolling_fleets: Mapped[list["PatrolledSystem"]] = relationship(
        "PatrolledSystem",
        back_populates="star_system",
    )


class PatrolledSystem(Base):
    __tablename__ = "patrolled_systems"

    star_system_id: Mapped[int] = mapped_column(
        ForeignKey("star_system.star_system_id"), primary_key=True
    )
    fleet_id: Mapped[int] = mapped_column(
        ForeignKey("fleet.fleet_id"), primary_key=True
    )
    last_patrol_date: Mapped[datetime.datetime] = mapped_column()

    star_system: Mapped["StarSystem"] = relationship(
        "StarSystem",
        back_populates="patrolling_fleets",
    )
    fleet: Mapped["Fleet"] = relationship(
        "Fleet",
        back_populates="patrolled_systems",
    )
