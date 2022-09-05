from mongoengine import *

class Wishes(Document):
    type = StringField(required=True)
    name = StringField(required=True)
    time = DateTimeField(required=True)
    stars = IntField(required=True)
    pity = IntField(required=True)
    roll_no = IntField(required=True)
    group = IntField(required=True)
    banner = StringField(required=True)
    wish_type = StringField(required=True)

    meta = {
        'indexes': [
            {'fields': ('name', 'time', 'roll_no'), 'unique': True, 'dropDups': True}
        ]
    }    

class Constellations(Document):
    constellation_id = IntField(required=True)
    character_name = StringField(required=True)
    icon = StringField(required=True)
    name = StringField(required=True)
    effect = StringField(required=True)
    activated = BooleanField(required=True)

class Weapons(Document):
    weapon_id = IntField(required=True)
    icon = StringField(required=True)
    name = StringField(required=True)
    rarity = IntField(required=True)
    description = StringField(required=True)
    level = IntField(required=True)
    type = StringField(required=True)
    ascension = IntField(required=True)
    refinement = IntField(required=True)

    meta = {
        'indexes': [
            {'fields': ('weapon_id',), 'unique': True, 'dropDups': True}
        ]
    }

class Characters(Document):
    character_id = IntField(required=True)
    name = StringField(required=True)
    element = StringField(required=True)
    rarity = IntField(required=True)
    icon = StringField(required=True)
    collab = BooleanField(required=True)
    level = IntField(required=True)
    friendship = IntField(required=True)
    constellation_level = IntField(required=True)
    constellations = ListField(ReferenceField(Constellations))
    weapon = ReferenceField(Weapons)

    meta = {
        'indexes': [
            {'fields': ('character_id',), 'unique': True, 'dropDups': True}
        ]
    }