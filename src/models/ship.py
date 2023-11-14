from src.database.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.fleet import Fleet


class SpaceshipClassification(Base):
    __tablename__ = "spaceship_classification"

    spaceship_classification_id: Mapped[int] = mapped_column(primary_key=True)
    spaceship_classification_name: Mapped[str] = mapped_column()

    spaceships: Mapped[list["Spaceship"]] = relationship(
        "Spaceship",
        back_populates="spaceship_classification",
    )


class Spaceship(Base):
    __tablename__ = "spaceship"

    spaceship_id: Mapped[int] = mapped_column(primary_key=True)
    spaceship_name: Mapped[str] = mapped_column()
    spaceship_fleet_id: Mapped[int] = mapped_column(
        ForeignKey("fleet.fleet_id")
    )
    spaceship_classification_id: Mapped[int] = mapped_column(
        ForeignKey("spaceship_classification.spaceship_classification_id")
    )
    spaceship_experience: Mapped[int] = mapped_column()

    fleet: Mapped["Fleet"] = relationship(
        "Fleet",
        back_populates="spaceships",
    )
    spaceship_classification: Mapped["SpaceshipClassification"] = relationship(
        "SpaceshipClassification",
        back_populates="spaceships",
    )
    spaceship_modules: Mapped[list["SpaceshipToModule"]] = relationship(
        "SpaceshipToModule",
        back_populates="spaceship",
    )


class SpaceshipModule(Base):
    __tablename__ = "spaceship_module"

    spaceship_module_id: Mapped[int] = mapped_column(primary_key=True)
    spaceship_module_name: Mapped[str] = mapped_column()
    spaceship_module_weight: Mapped[int] = mapped_column()
    spaceship_module_power: Mapped[int] = mapped_column()
    spaceship_module_trade_protection: Mapped[int] = mapped_column()

    spaceship_to_module: Mapped[list["SpaceshipToModule"]] = relationship(
        "SpaceshipToModule",
        back_populates="spaceship_module",
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

    spaceship: Mapped["Spaceship"] = relationship(
        "Spaceship",
        back_populates="spaceship_modules",
    )
    spaceship_module: Mapped["SpaceshipModule"] = relationship(
        "SpaceshipModule",
        back_populates="spaceship_to_module",
    )


class SpaceshipRank(Base):
    __tablename__ = "spaceship_rank"

    spaceship_rank_id: Mapped[int] = mapped_column(primary_key=True)
    spaceship_rank_name: Mapped[str] = mapped_column()
    spaceship_min_experience: Mapped[int] = mapped_column()
    spaceship_max_experience: Mapped[int] = mapped_column()


class SpaceshipWeightClass(Base):
    __tablename__ = "spaceship_weight_class"

    spaceship_weight_class_id: Mapped[int] = mapped_column(primary_key=True)
    spaceship_weight_class_name: Mapped[str] = mapped_column()
    spaceship_min_weight: Mapped[int] = mapped_column()
    spaceship_max_weight: Mapped[int] = mapped_column()
    spaceship_command_cost: Mapped[int] = mapped_column()
