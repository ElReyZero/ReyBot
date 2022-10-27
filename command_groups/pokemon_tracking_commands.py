from discord import app_commands, Attachment, Interaction
from database.query_scripts.pokemon import mark_pokemon, get_pkmn_entry, import_dex
from typing import Literal
import config as cfg
import os

class PokemonTracker(app_commands.Group, name="pkmn_tracker", description="Commands Related to Pokemon Tracking"):

    @app_commands.command(name="mark_pokemon", description="Marks a pokemon as obtained")
    async def mark_pokemon(self, interaction: Interaction, pokemon_name: str, ability: str, shiny:Literal["Yes", "No"]="No", regional: Literal["Yes", "No"]="No"):
        await interaction.response.defer()
        if shiny == "Yes":
            shiny = True
        else:
            shiny = False
        if regional == "Yes":
            regional = True
        else:
            regional = False
        result = await mark_pokemon(pokemon_name.capitalize(), interaction.user.id, ability, shiny, regional)
        if result is None:
            await interaction.followup.send(f"There is no pokemon named {pokemon_name.capitalize()}")
        elif result:
            await interaction.followup.send(f"Marked {pokemon_name.capitalize()} as obtained")
        else:
            await interaction.followup.send(f"You already have {pokemon_name.capitalize()} marked as obtained")

    @app_commands.command(name="import_dex", description="Imports your dex from an excel file")
    async def import_dex(self, interaction: Interaction, dex_file: Attachment):
        await interaction.response.defer()
        if not dex_file.filename.endswith(".xlsx"):
            await interaction.followup.send("Please upload a valid excel file")
            return
        filepath = cfg.PROJECT_PATH +'/temp/dex.xlsx'
        await dex_file.save(filepath)
        try:
            await import_dex(interaction.user.id, filepath)
            await interaction.followup.send("Successfully imported your dex")
        except ValueError:
            await interaction.followup.send("Please upload a valid excel file")
        if os.path.exists(filepath):
            os.remove(filepath)

    @app_commands.command(name="catched_pokemon", description="Gets all the pokemon you have marked as obtained")
    async def get_catched_pokemon(self, interaction):
        await interaction.response.send_message("This command is not yet implemented")
        pass

    @app_commands.command(name="check_pokemon", description="Checks if you have a pokemon marked as obtained")
    async def check_pokemon(self, interaction: Interaction, pokemon_name: str):
        await interaction.response.defer()
        result = await get_pkmn_entry(interaction.user.id, pokemon_name.capitalize())
        if not result:
            await interaction.followup.send(f"You don't have {pokemon_name.capitalize()}")
        else:
            pokemon = result[0].to_mongo()
            entry = result[1].to_mongo()
            await interaction.followup.send(f"You own {pokemon_name.capitalize()}\nAbility: {entry['ability']}\nShiny: {entry['shiny']}\nRegional: {entry['regional']}")