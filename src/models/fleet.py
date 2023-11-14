from typing import TYPE_CHECKING

from src.database.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.models.empire import Empire
    from src.models.ship import Spaceship
    from src.models.star_system import PatrolledSystem


class Fleet(Base):
    __tablename__ = "fleet"

    fleet_id: Mapped[int] = mapped_column(primary_key=True)
    fleet_name: Mapped[str] = mapped_column()
    empire_id: Mapped[int] = mapped_column(ForeignKey("empire.empire_id"))

    empire: Mapped["Empire"] = relationship(
        "Empire",
        back_populates="fleets",
    )
    spaceships: Mapped[list["Spaceship"]] = relationship(
        "Spaceship",
        back_populates="fleet",
    )
    patrolled_systems: Mapped[list["PatrolledSystem"]] = relationship(
        "PatrolledSystem",
        back_populates="fleet",
    )
