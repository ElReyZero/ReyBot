from utils.threading import to_thread
from database.models.pokemon import PokemonEntry, Pokemon
import pandas as pd
import logging

log = logging.getLogger('discord')

@to_thread
def push_all_pokemons():
    df = pd.read_csv("./database/raw_data/pokemon.csv")
    columns_to_mongo = ["pokedex_number", "name", "type1", "type2", "generation"]
    df = df[columns_to_mongo]
    pokemon_instances = [Pokemon(**data) for data in df.to_dict('records')]
    Pokemon.objects.insert(pokemon_instances)

@to_thread
def mark_pokemon(pokemon_name: str, user: str, ability: str, shiny: str, regional: str):
    pokemon = Pokemon.objects(name=pokemon_name).first()
    if pokemon is None:
        return None
    pokemon_entry = PokemonEntry.objects(pokemon=pokemon, user=user).first()
    if pokemon_entry is not None:
        return False
    else:
        pokemon_entry = PokemonEntry(pokemon=pokemon, ability=ability, shiny=shiny, regional=regional, user=user)
        pokemon_entry.save()
        return True

@to_thread
def get_pkmn_entries(user: str):
    pokemon_entries = PokemonEntry.objects(user=user)
    pokemon = [pokemon_entry.pokemon for pokemon_entry in pokemon_entries]
    return pokemon

@to_thread
def get_pkmn_entry(user:str, pokemon_name:str):
    pokemon = Pokemon.objects(name=pokemon_name).first()
    if not pokemon:
        return None
    pokemon_entry = PokemonEntry.objects(pokemon=pokemon, user=user).first()
    if not pokemon_entry:
        return None
    return [pokemon, pokemon_entry]

@to_thread
def import_dex(user:str, filepath:str):
    df = pd.read_excel(filepath)
    for column in ["Obtained", "Shiny", "Regional"]:
        df[column] = df[column].apply(lambda x : True if x == "X" else False)
    df["Ability"] = df["Ability"].apply(lambda x : x if not pd.isna(x) else "")
    for index, row in df.iterrows():
        pokemon = Pokemon.objects(name=row["Pokemon"]).first()
        if pokemon is None or not row["Obtained"]:
            continue
        pokemon_entry = PokemonEntry.objects(pokemon=pokemon, user=user).first()
        if not pokemon_entry:
            pokemon_entry = PokemonEntry(pokemon=pokemon, ability=row["Ability"], shiny=row["Shiny"], regional=row["Regional"], user=user)
            pokemon_entry.save()
        else:
            pokemon_entry.ability = row["Ability"]
            pokemon_entry.shiny = row["Shiny"]
            pokemon_entry.regional = row["Regional"]
            pokemon_entry.save()