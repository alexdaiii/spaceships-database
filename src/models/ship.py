from src.database.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class ShipClass(Base):
    __tablename__ = "ship_class"

    ship_class_id: Mapped[int] = mapped_column(primary_key=True)
    ship_class_name: Mapped[str]
    ship_class_bonus: Mapped[float | None]


class Spaceship(Base):
    __tablename__ = "spaceship"

    spaceship_id: Mapped[int] = mapped_column(primary_key=True)
    spaceship_name: Mapped[str]
    spaceship_fleet_id: Mapped[int] = mapped_column(
        ForeignKey("fleet.fleet_id")
    )
    spaceship_class_id: Mapped[int] = mapped_column(
        ForeignKey("ship_class.ship_class_id")
    )
    spaceship_experience: Mapped[int | None]


class SpaceshipModule(Base):
    __tablename__ = "spaceship_module"

    spaceship_module_id: Mapped[int] = mapped_column(primary_key=True)
    spaceship_module_name: Mapped[str]
    spaceship_module_weight: Mapped[int]
    spaceship_module_power: Mapped[int | None]
    spaceship_module_trade_protection: Mapped[int | None]


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
    spaceship_rank_name: Mapped[str]
    spaceship_min_experience: Mapped[int]
    spaceship_max_experience: Mapped[int]


__all__ = [
    "ShipClass",
    "Spaceship",
    "SpaceshipModule",
    "SpaceshipToModule",
    "SpaceshipRank",
]
