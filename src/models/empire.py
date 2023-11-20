from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
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


class Empire(Base):
    __tablename__ = "empire"

    empire_id: Mapped[int] = mapped_column(primary_key=True)
    empire_name: Mapped[str] = mapped_column(String(255), unique=True)
    empire_authority_id: Mapped[int] = mapped_column(
        ForeignKey("empire_authority.empire_authority_id")
    )
    empire_score: Mapped[int | None]

    fleets: Mapped[list["Fleet"]] = relationship(
        "Fleet", back_populates="empire"
    )
    star_systems: Mapped[list["StarSystem"]] = relationship(
        "StarSystem",
        back_populates="empire",
    )


class EmpireToEthic(Base):
    __tablename__ = "empire_to_ethic"

    empire_id: Mapped[int] = mapped_column(
        ForeignKey("empire.empire_id"), primary_key=True
    )
    empire_ethic_id: Mapped[int] = mapped_column(
        ForeignKey("empire_ethic.empire_ethic_id"), primary_key=True
    )
    empire_ethic_attraction: Mapped[int] = mapped_column(default=0)

    empire: Mapped["Empire"] = relationship("Empire")
    empire_ethic: Mapped["EmpireEthic"] = relationship("EmpireEthic")


__all__ = [
    "EmpireAuthority",
    "EmpireEthic",
    "Empire",
    "EmpireToEthic",
]
