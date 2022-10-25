from mongoengine import *

class Pokemon(Document):
    pokedex_number = IntField(required=True)
    name = StringField(required=True)
    type1 = StringField(required=True)
    type2 = StringField(required=True)
    generation = IntField(required=True)
    meta = {"db_alias": "pokemon"}

class PokemonEntry(Document):
    pokemon = ReferenceField(Pokemon)
    ability = StringField(default=None)
    shiny = BooleanField(default=False)
    regional = BooleanField(default=False)
    user = IntField(required=True)

    meta = {"db_alias": "pokemon"}