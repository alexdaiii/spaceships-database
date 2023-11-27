from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.models import Fleet
    from src.models.star_system import StarSystem


class EmpireAuthority(Base):
    __tablename__ = "empire_authority"

    empire_authority_id: Mapped[int] = mapped_column(primary_key=True)
    empire_authority_name: Mapped[str] = mapped_column(
        String(255), unique=True
    )

    empire: Mapped[list["Empire"]] = relationship("Empire")


class EmpireEthic(Base):
    __tablename__ = "empire_ethic"

    empire_ethic_id: Mapped[int] = mapped_column(primary_key=True)
    empire_ethic_name: Mapped[str] = mapped_column(String(255), unique=True)

    empires: Mapped[list["Empire"]] = relationship(
        secondary="empire_to_ethic",
        back_populates="ethics",
    )


class Empire(Base):
    __tablename__ = "empire"

    empire_id: Mapped[int] = mapped_column(primary_key=True)
    empire_name: Mapped[str] = mapped_column(String(255), unique=True)
    empire_authority_id: Mapped[int] = mapped_column(
        ForeignKey("empire_authority.empire_authority_id")
    )
    empire_score: Mapped[int] = mapped_column(default=0)

    fleets: Mapped[list["Fleet"]] = relationship(
        "Fleet", back_populates="empire"
    )
    star_systems: Mapped[list["StarSystem"]] = relationship(
        "StarSystem",
        back_populates="empire",
    )
    ethics: Mapped[list["EmpireEthic"]] = relationship(
        secondary="empire_to_ethic",
        back_populates="empires",
        cascade="all, delete",
        passive_deletes=True,
    )


class EmpireToEthic(Base):
    __tablename__ = "empire_to_ethic"

    empire_id: Mapped[int] = mapped_column(
        ForeignKey("empire.empire_id", ondelete="CASCADE"),
        primary_key=True,
    )
    empire_ethic_id: Mapped[int] = mapped_column(
        ForeignKey("empire_ethic.empire_ethic_id"), primary_key=True
    )
    empire_ethic_attraction: Mapped[int] = mapped_column(default=0)

    # check constraint - empire_ethic_attraction cannot be negative
    # or greater than 3
    __table_args__ = (
        CheckConstraint(
            "empire_ethic_attraction >= 0 AND empire_ethic_attraction <= 3",
            name="empire_to_ethic_empire_ethic_attraction_check",
        ),
    )


__all__ = [
    "EmpireAuthority",
    "EmpireEthic",
    "Empire",
    "EmpireToEthic",
]
