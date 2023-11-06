"""
CREATE TABLE fleet (
    fleet_id INTEGER PRIMARY KEY,
    fleet_name VARCHAR NOT NULL,
    empire_id INTEGER NOT NULL,

    FOREIGN KEY (empire_id) REFERENCES empire (empire_id)
);
"""
from typing import TYPE_CHECKING

from src.database.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.models.empire import Empire


class Fleet(Base):
    __tablename__ = "fleet"

    fleet_id: Mapped[int] = mapped_column(primary_key=True)
    fleet_name: Mapped[str] = mapped_column()
    empire_id: Mapped[int] = mapped_column(ForeignKey("empire.empire_id"))

    empire: Mapped["Empire"] = relationship(
        "Empire",
        back_populates="fleets",
    )

    def __repr__(self):
        return (
            f"<Fleet("
            f"fleet_id={self.fleet_id}, "
            f"fleet_name={self.fleet_name}, "
            f"empire_id={self.empire_id}"
            f")>"
        )

    def __str__(self):
        return self.fleet_name
