#pylint: disable=too-few-public-methods, unsubscriptable-object
from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.schema import MetaData


class GenshinBase(DeclarativeBase):
    metadata = MetaData(schema='genshin')

class Wish(GenshinBase):
    __tablename__ = 'wishes'

    id : Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    time: Mapped[datetime] = mapped_column(primary_key=True, nullable=False)
    stars: Mapped[int] = mapped_column(nullable=False)
    pity: Mapped[int] = mapped_column(nullable=False)
    roll_no: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    group: Mapped[int] = mapped_column(nullable=False)
    banner: Mapped[str] = mapped_column(nullable=False)
    wish_type: Mapped[str] = mapped_column(nullable=False)

class Constellation(GenshinBase):
    __tablename__ = 'constellations'

    id: Mapped[int] = mapped_column(primary_key=True)
    constellation_id: Mapped[int] = mapped_column(nullable=False)
    character_name: Mapped[str] = mapped_column(nullable=False)
    icon: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    effect: Mapped[str] = mapped_column(nullable=False)
    activated: Mapped[bool] = mapped_column(nullable=False)
    character_id: Mapped[int] = mapped_column(ForeignKey('characters.id'))


class Weapon(GenshinBase):
    __tablename__ = 'weapons'

    id: Mapped[int] = mapped_column(primary_key=True)
    weapon_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    icon: Mapped[str] = mapped_column(nullable=False)
    name : Mapped[str] = mapped_column(nullable=False)
    rarity : Mapped[int] = mapped_column(nullable=False)
    level : Mapped[int] = mapped_column(nullable=False)
    type : Mapped[str] = mapped_column(nullable=False)
    refinement : Mapped[int] = mapped_column(nullable=False)

class Character(GenshinBase):
    __tablename__ = 'characters'

    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    name : Mapped[str] = mapped_column(nullable=False)
    element : Mapped[str] = mapped_column(nullable=False)
    rarity : Mapped[int] = mapped_column(nullable=False)
    icon : Mapped[str] = mapped_column(nullable=False)
    collab : Mapped[bool] = mapped_column(nullable=False)
    level : Mapped[int] = mapped_column(nullable=False)
    friendship : Mapped[int] = mapped_column(nullable=False)
    constellation_level: Mapped[int] = mapped_column(nullable=False)
    weapon_id: Mapped[int] = mapped_column(ForeignKey('weapons.id'))

    constellations: Mapped[List["Constellation"]] = relationship(backref='character', cascade='all, delete-orphan')

    weapon: Mapped["Weapon"] = relationship(backref='character')
