from src.database.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class EmpireAuthority(Base):
    __tablename__ = "empire_authority"

    empire_authority_id: Mapped[int] = mapped_column(primary_key=True)
    empire_authority_name: Mapped[str]


class EmpireEthic(Base):
    __tablename__ = "empire_ethic"

    empire_ethic_id: Mapped[int] = mapped_column(primary_key=True)
    empire_ethic_name: Mapped[str] = mapped_column()


class Empire(Base):
    __tablename__ = "empire"

    empire_id: Mapped[int] = mapped_column(primary_key=True)
    empire_name: Mapped[str]
    empire_authority_id: Mapped[int] = mapped_column(
        ForeignKey("empire_authority.empire_authority_id")
    )
    empire_score: Mapped[int | None]


class EmpireToEthic(Base):
    __tablename__ = "empire_to_ethic"

    empire_id: Mapped[int] = mapped_column(
        ForeignKey("empire.empire_id"), primary_key=True
    )
    empire_ethic_id: Mapped[int] = mapped_column(
        ForeignKey("empire_ethic.empire_ethic_id"), primary_key=True
    )
    empire_ethic_attraction: Mapped[int] = mapped_column(default=0)


__all__ = [
    "EmpireAuthority",
    "EmpireEthic",
    "Empire",
    "EmpireToEthic",
]
