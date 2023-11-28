from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class ShipClass(Base):
    __tablename__ = "ship_class"

    ship_class_id: Mapped[int] = mapped_column(primary_key=True)
    ship_class_name: Mapped[str] = mapped_column(String(255), unique=True)

    small_component_slots: Mapped[int] = mapped_column(default=0)
    medium_component_slots: Mapped[int] = mapped_column(default=0)
    large_component_slots: Mapped[int] = mapped_column(default=0)
    xlarge_component_slots: Mapped[int] = mapped_column(default=0)
    titan_component_slots: Mapped[int] = mapped_column(default=0)
    juggernaut_component_slots: Mapped[int] = mapped_column(default=0)
    colossus_component_slots: Mapped[int] = mapped_column(default=0)
    star_eater_component_slots: Mapped[int] = mapped_column(default=0)

    templates: Mapped[list["ShipTemplate"]] = relationship(
        "ShipTemplate",
    )


class ShipTemplate(Base):
    __tablename__ = "ship_template"

    ship_template_id: Mapped[int] = mapped_column(primary_key=True)
    ship_class_id: Mapped[int] = mapped_column(
        ForeignKey("ship_class.ship_class_id")
    )
    ship_template_name: Mapped[str] = mapped_column(String(255), unique=True)

    template_modules: Mapped[list["SpaceshipModule"]] = relationship(
        secondary="ship_template_to_module",
        back_populates="ship_templates_using",
    )
    ships_using: Mapped[list["Spaceship"]] = relationship(
        "Spaceship",
    )


class SpaceshipModule(Base):
    __tablename__ = "spaceship_module"

    spaceship_module_id: Mapped[int] = mapped_column(primary_key=True)
    spaceship_module_name: Mapped[str] = mapped_column(
        String(255), unique=True
    )
    spaceship_module_power: Mapped[int]

    small_component_slots: Mapped[int] = mapped_column(default=0)
    medium_component_slots: Mapped[int] = mapped_column(default=0)
    large_component_slots: Mapped[int] = mapped_column(default=0)
    xlarge_component_slots: Mapped[int] = mapped_column(default=0)
    titan_component_slots: Mapped[int] = mapped_column(default=0)
    juggernaut_component_slots: Mapped[int] = mapped_column(default=0)
    colossus_component_slots: Mapped[int] = mapped_column(default=0)
    star_eater_component_slots: Mapped[int] = mapped_column(default=0)

    ship_templates_using: Mapped[list["ShipTemplate"]] = relationship(
        secondary="ship_template_to_module",
        back_populates="template_modules",
    )

    # check constraint - sum of component slots must be = 1
    # no slots can be negative
    __table_args__ = (
        CheckConstraint(
            "small_component_slots + "
            "medium_component_slots + "
            "large_component_slots + "
            "xlarge_component_slots + "
            "titan_component_slots + "
            "juggernaut_component_slots + "
            "colossus_component_slots + "
            "star_eater_component_slots = 1",
            "spaceship_module_slots_only_one_size_check",
        ),
        CheckConstraint(
            "small_component_slots >= 0 "
            "AND medium_component_slots >= 0 "
            "AND large_component_slots >= 0 "
            "AND xlarge_component_slots >= 0 "
            "AND titan_component_slots >= 0 "
            "AND juggernaut_component_slots >= 0 "
            "AND colossus_component_slots >= 0 "
            "AND star_eater_component_slots >= 0",
            "spaceship_module_slots_positive_check",
        ),
    )


class ShipTemplateModule(Base):
    __tablename__ = "ship_template_to_module"

    ship_template_id: Mapped[int] = mapped_column(
        ForeignKey("ship_template.ship_template_id"), primary_key=True
    )
    ship_module_id: Mapped[int] = mapped_column(
        ForeignKey("spaceship_module.spaceship_module_id"), primary_key=True
    )
    ship_module_count: Mapped[int] = mapped_column(default=0)

    # check constraint - spaceship_module_count cannot be negative
    __table_args__ = (
        CheckConstraint(
            "ship_module_count > 0",
            "ship_module_count_positive_check",
        ),
    )


class Spaceship(Base):
    __tablename__ = "spaceship"

    spaceship_id: Mapped[int] = mapped_column(primary_key=True)
    spaceship_name: Mapped[str] = mapped_column(String(255))
    spaceship_fleet_id: Mapped[int] = mapped_column(
        ForeignKey("fleet.fleet_id")
    )
    spaceship_template_id: Mapped[int] = mapped_column(
        ForeignKey("ship_template.ship_template_id")
    )
    spaceship_experience: Mapped[int | None]


class SpaceshipRank(Base):
    __tablename__ = "spaceship_rank"

    spaceship_rank_id: Mapped[int] = mapped_column(primary_key=True)
    spaceship_rank_name: Mapped[str] = mapped_column(String(255), unique=True)
    spaceship_min_experience: Mapped[int]
    spaceship_max_experience: Mapped[int]


__all__ = [
    "ShipClass",
    "ShipTemplate",
    "SpaceshipModule",
    "ShipTemplateModule",
    "Spaceship",
    "SpaceshipRank",
]
