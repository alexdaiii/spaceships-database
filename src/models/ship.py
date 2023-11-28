from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class ShipClass(Base):
    __tablename__ = "ship_class"

    ship_class_id: Mapped[int] = mapped_column(primary_key=True)
    ship_class_name: Mapped[str] = mapped_column(String(255), unique=True)
    ship_command_points: Mapped[int]

    ships: Mapped[list["Spaceship"]] = relationship("Spaceship")


class Spaceship(Base):
    __tablename__ = "spaceship"

    spaceship_id: Mapped[int] = mapped_column(primary_key=True)
    spaceship_name: Mapped[str] = mapped_column(String(255))
    spaceship_fleet_id: Mapped[int] = mapped_column(
        ForeignKey("fleet.fleet_id")
    )
    spaceship_class_id: Mapped[int] = mapped_column(
        ForeignKey("ship_class.ship_class_id")
    )
    spaceship_experience: Mapped[int | None]

    spaceship_modules: Mapped[list["SpaceshipModule"]] = relationship(
        secondary="spaceship_to_module", back_populates="spaceships"
    )


class SpaceshipModule(Base):
    __tablename__ = "spaceship_module"

    spaceship_module_id: Mapped[int] = mapped_column(primary_key=True)
    spaceship_module_name: Mapped[str] = mapped_column(
        String(255), unique=True
    )
    spaceship_module_power: Mapped[int]

    spaceships: Mapped[list["Spaceship"]] = relationship(
        secondary="spaceship_to_module", back_populates="spaceship_modules"
    )


class SpaceshipToModule(Base):
    __tablename__ = "spaceship_to_module"

    spaceship_id: Mapped[int] = mapped_column(
        ForeignKey("spaceship.spaceship_id"),
        primary_key=True,
    )
    spaceship_module_id: Mapped[int] = mapped_column(
        ForeignKey("spaceship_module.spaceship_module_id"),
        primary_key=True,
    )


class SpaceshipRank(Base):
    __tablename__ = "spaceship_rank"

    spaceship_rank_id: Mapped[int] = mapped_column(primary_key=True)
    spaceship_rank_name: Mapped[str] = mapped_column(String(255), unique=True)
    spaceship_min_experience: Mapped[int]
    spaceship_max_experience: Mapped[int]


__all__ = [
    "ShipClass",
    "Spaceship",
    "SpaceshipModule",
    "SpaceshipToModule",
    "SpaceshipRank",
]
