from src.database.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.fleet import Fleet
    from src.models.star_system import StarSystem


class EmpireAuthority(Base):
    __tablename__ = "empire_authority"

    empire_authority_id: Mapped[int] = mapped_column(primary_key=True)
    empire_authority_name: Mapped[str]

    empires: Mapped[list["Empire"]] = relationship(
        "Empire",
        back_populates="empire_authority",
    )

    def __repr__(self):
        return (
            f"<EmpireAuthority("
            f"empire_authority_id={self.empire_authority_id}, "
            f"empire_authority_name={self.empire_authority_name}"
            f")>"
        )

    def __str__(self):
        return self.empire_authority_name


class EmpireEthic(Base):
    __tablename__ = "empire_ethic"

    empire_ethic_id: Mapped[int] = mapped_column(primary_key=True)
    empire_ethic_name: Mapped[str] = mapped_column()

    empires: Mapped[list["EmpireToEthic"]] = relationship(
        back_populates="empire_ethics",
    )


class Empire(Base):
    __tablename__ = "empire"

    empire_id: Mapped[int] = mapped_column(primary_key=True)
    empire_name: Mapped[str]
    empire_authority_id: Mapped[int] = mapped_column(
        ForeignKey("empire_authority.empire_authority_id")
    )

    empire_authority: Mapped[EmpireAuthority] = relationship(
        back_populates="empires"
    )
    empire_ethics: Mapped[list["EmpireToEthic"]] = relationship(
        back_populates="empires",
    )
    fleets: Mapped[list["Fleet"]] = relationship(
        back_populates="empire",
    )
    star_systems: Mapped[list["StarSystem"]] = relationship(
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

    empires: Mapped[list[Empire]] = relationship(
        back_populates="empire_ethics",
    )
    empire_ethics: Mapped[list[EmpireEthic]] = relationship(
        back_populates="empires",
    )
