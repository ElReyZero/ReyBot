from fireo.typedmodels import TypedModel
from fireo.fields import ReferenceField
from typing import List

class Weapon(TypedModel):
    weapon_id : int
    icon : str
    name : str
    rarity : int
    description : str
    level : int
    type : str
    ascension : int
    refinement : int

    class Meta:
        collection_name = "genshin_weapons"

class Constellation(TypedModel):
    constellation_id : int
    character_name : str
    icon : str
    name : str
    effect : str
    activated : bool

    class Meta:
        collection_name = "genshin_constellations"

class Character(TypedModel):
    character_id: int
    name: str
    element: str
    rarity: int
    icon: str
    collab: bool
    level: int
    friendship: int
    constellation_level: int
    constellations : List[Constellation]
    weapon : Weapon

    class Meta:
        collection_name = "genshin_characters"