from src.database.base import Base
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models import Spaceship


class Fleet(Base):
    __tablename__ = "fleet"

    fleet_id: Mapped[int] = mapped_column(primary_key=True)
    fleet_name: Mapped[str] = mapped_column(String(255))
    fleet_empire_owner: Mapped[int] = mapped_column(
        ForeignKey("empire.empire_id")
    )
    fleet_cloak_strength: Mapped[int]
    fleet_is_docked: Mapped[bool]

    ships: Mapped[list["Spaceship"]] = relationship("Spaceship")


__all__ = [
    "Fleet",
]
