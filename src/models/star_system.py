from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from .empire import Empire


class StarType(Base):
    __tablename__ = "star_type"

    star_type_id: Mapped[int] = mapped_column(primary_key=True)
    star_type_name: Mapped[str] = mapped_column(String(255), unique=True)
    star_type_habitability: Mapped[float]

    stars: Mapped[list["StarSystem"]] = relationship(
        "StarSystem",
    )


class StarSystem(Base):
    __tablename__ = "star_system"

    star_system_id: Mapped[int] = mapped_column(primary_key=True)
    star_system_name: Mapped[str] = mapped_column(String(255), unique=True)
    system_is_choke_point: Mapped[bool | None]
    empire_owner: Mapped[int | None] = mapped_column(
        ForeignKey("empire.empire_id"), nullable=True
    )
    star_type_id: Mapped[int] = mapped_column(
        ForeignKey("star_type.star_type_id")
    )

    planets: Mapped[list["Planet"]] = relationship(
        "Planet",
        back_populates="star_system",
    )
    star_type: Mapped[StarType] = relationship(
        "StarType",
        back_populates="stars",
    )
    empire: Mapped["Empire"] = relationship(
        "Empire",
        back_populates="star_systems",
    )


class Biome(Base):
    __tablename__ = "biome"

    biome_id: Mapped[int] = mapped_column(primary_key=True)
    biome_name: Mapped[str] = mapped_column(String(255), unique=True)
    biome_is_habitable: Mapped[bool]

    planets: Mapped[list["Planet"]] = relationship(
        "Planet",
        back_populates="biome",
    )


class Planet(Base):
    __tablename__ = "planet"

    planet_id: Mapped[int] = mapped_column(primary_key=True)
    planet_name: Mapped[str] = mapped_column(String(255), unique=True)
    planet_biome: Mapped[int] = mapped_column(ForeignKey("biome.biome_id"))
    planet_star_system: Mapped[int] = mapped_column(
        ForeignKey("star_system.star_system_id")
    )
    planet_size: Mapped[int]
    planet_pops: Mapped[int] = mapped_column(default=0)
    planet_trade_value: Mapped[int] = mapped_column(default=0)
    planet_energy_value: Mapped[int] = mapped_column(default=0)
    planet_research_value: Mapped[int] = mapped_column(default=0)
    planet_minerals_value: Mapped[int] = mapped_column(default=0)

    biome: Mapped[Biome] = relationship(
        "Biome",
        back_populates="planets",
    )
    star_system: Mapped[StarSystem] = relationship(
        "StarSystem",
        back_populates="planets",
    )


__all__ = [
    "StarSystem",
    "Biome",
    "Planet",
    "StarType",
]
