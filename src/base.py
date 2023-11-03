from typing import TYPE_CHECKING

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

if TYPE_CHECKING:  # pragma: no cover
    from dataclasses import dataclass as t_dataclass
else:
    t_dataclass = lambda x: x  # noqa: E731


class Base(DeclarativeBase):
    metadata = meta

    pass
