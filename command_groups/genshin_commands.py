from random import randint
from discord import app_commands, Attachment, Interaction
import config as cfg
import genshin as gi
from database.crud.genshin import push_characters, push_all_wishes, get_character_and_weapon, get_weapon_by_obj_id, get_all_characters
from discord_tools.embeds import genshin_character_embed
from discord_tools.views.genshin_views import AllCharactersView, WeaponView
import os

class GenshinDB(app_commands.Group, name="genshin_db", description="Commands Related to Genshin Impact's custom persistence"):

    @app_commands.command(name="push_characters", description="Push all current characters to the database")
    async def push_characters(self, interaction: Interaction):
        client = gi.Client()
        await interaction.response.send_message("Pushing characters...")
        if interaction.user.id == int(cfg.MAIN_ADMIN_ID):
            client.set_cookies(
                ltuid=cfg.genshin_data["ltuid"], ltoken=cfg.genshin_data["ltoken"])
            chars = await client.get_genshin_characters(cfg.genshin_data["uuid"])
            await push_characters(chars)
            await interaction.followup.send("Successfully pushed all characters to database", ephemeral=True)

    @app_commands.command(name="get_character", description="Get a character from the database")
    async def get_character(self, interaction: Interaction, name: str):
        await interaction.response.defer()
        character, weapon = await get_character_and_weapon(name)
        if character:
            view = WeaponView(character, weapon)
            embed = genshin_character_embed(character)
            await interaction.followup.send(embed=embed, view=view)
        else:
            await interaction.followup.send(f"Character called {name} not found", ephemeral=True)

    @app_commands.command(name="get_all_characters", description="Get all characters from the database")
    async def get_all_characters(self, interaction: Interaction):
        await interaction.response.defer()
        characters = await get_all_characters()
        if characters:
            view = AllCharactersView(characters)
            embed = genshin_character_embed(
                characters[randint(0, len(characters)-1)])
            await interaction.followup.send(embed=embed, view=view)
        else:
            await interaction.followup.send(f"No characters found", ephemeral=True)

    @app_commands.command(name="push_wishes", description="Push an excel file of all wishes to the database")
    async def get_wishes(self, interaction: Interaction, wishes_file: Attachment):
        await interaction.response.defer()
        if not wishes_file.filename.endswith(".xlsx"):
            await interaction.followup.send("Please upload a valid excel file")
            return
        filepath = cfg.PROJECT_PATH + '/temp/wishes.xlsx'
        await wishes_file.save(filepath)
        if not os.path.exists(filepath):
            await interaction.followup.send("Error saving file")
            return
        try:
            if interaction.user.id == int(cfg.MAIN_ADMIN_ID):
                await push_all_wishes(filepath)
                await interaction.followup.send("Wishes pushed to database", ephemeral=True)
        except ValueError:
            await interaction.followup.send("Please upload a valid excel file")
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
