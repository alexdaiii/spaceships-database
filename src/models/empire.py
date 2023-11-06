"""
CREATE TABLE empire_authority (
    empire_authority_id INTEGER PRIMARY KEY,
    empire_authority_name VARCHAR NOT NULL
);

CREATE TABLE empire_ethic (
    empire_ethic_id INTEGER PRIMARY KEY,
    empire_ethic_name VARCHAR NOT NULL
    empire_ethic_attraction INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE empire (
    empire_id INTEGER PRIMARY KEY,
    empire_name VARCHAR NOT NULL,
    empire_authority_id INTEGER NOT NULL,

    FOREIGN KEY (empire_authority_id) REFERENCES empire_authority (empire_authority_id)
);

CREATE TABLE empire_to_ethic (
    empire_id INTEGER NOT NULL,
    empire_ethic_id INTEGER NOT NULL,

    FOREIGN KEY (empire_id) REFERENCES empire (empire_id),
    PRIMARY KEY (empire_id, empire_ethic_id)
);
"""
from src.database.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


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

    def __repr__(self):
        return (
            f"<EmpireEthic("
            f"empire_ethic_id={self.empire_ethic_id}, "
            f"empire_ethic_name={self.empire_ethic_name}"
            f")>"
        )

    def __str__(self):
        return self.empire_ethic_name


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

    def __repr__(self):
        return (
            f"<Empire("
            f"empire_id={self.empire_id}, "
            f"empire_name={self.empire_name}, "
            f"empire_authority_id={self.empire_authority_id}"
            f")>"
        )

    def __str__(self):
        return self.empire_name


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

    def __repr__(self):
        return (
            f"<EmpireToEthic(empire_id={self.empire_id}, "
            f"empire_ethic_id={self.empire_ethic_id}, "
            f"empire_ethic_attraction={self.empire_ethic_attraction}"
            f")>"
        )

    def __str__(self):
        return f"{self.empire_id} {self.empire_ethic_id}"
