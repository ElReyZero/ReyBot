from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.schema import MetaData

GenshinBase = declarative_base(metadata=MetaData(schema='genshin'))

class Wish(GenshinBase):
    __tablename__ = 'wishes'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    time = Column(DateTime, primary_key=True, nullable=False)
    stars = Column(Integer, nullable=False)
    pity = Column(Integer, nullable=False)
    roll_no = Column(Integer, primary_key=True, nullable=False)
    group = Column(Integer, nullable=False)
    banner = Column(String, nullable=False)
    wish_type = Column(String, nullable=False)

class Constellation(GenshinBase):
    __tablename__ = 'constellations'

    id = Column(Integer, primary_key=True)
    constellation_id = Column(Integer, nullable=False)
    character_name = Column(String, nullable=False)
    icon = Column(String, nullable=False)
    name = Column(String, nullable=False)
    effect = Column(String, nullable=False)
    activated = Column(Boolean, nullable=False)
    character_id = Column(Integer, ForeignKey('characters.id'))


class Weapon(GenshinBase):
    __tablename__ = 'weapons'

    id = Column(Integer, primary_key=True)
    weapon_id = Column(Integer, nullable=False, unique=True)
    icon = Column(String, nullable=False)
    name = Column(String, nullable=False)
    rarity = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    ascension = Column(Integer, nullable=False)
    refinement = Column(Integer, nullable=False)

class Character(GenshinBase):
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, nullable=False, unique=True)
    name = Column(String, nullable=False)
    element = Column(String, nullable=False)
    rarity = Column(Integer, nullable=False)
    icon = Column(String, nullable=False)
    collab = Column(Boolean, nullable=False)
    level = Column(Integer, nullable=False)
    friendship = Column(Integer, nullable=False)
    constellation_level = Column(Integer, nullable=False)
    weapon_id = Column(Integer, ForeignKey('weapons.id'))

    constellations = relationship('Constellation', backref='character', cascade='all, delete-orphan')

    weapon = relationship('Weapon', backref='character')
