from discord import app_commands, Attachment, ButtonStyle
import discord.ui as ui
import config as cfg
import genshin as gi
from database.query_scripts.genshin import pushCharacters, push_all_wishes, getCharacter, getWeaponByObjId
from discord_tools.embeds import genshinCharacterEmbed, genshinWeaponEmbed
from discord_tools.views.genshin_views import WeaponView
import os

class GenshinDB(app_commands.Group, name="genshin_db", description="Commands Related to Genshin Impact's custom persistence"):

    @app_commands.command(name="push_characters", description="Push all current characters to the database")
    async def push_characters(self, interaction):
        client = gi.Client()
        await interaction.response.send_message("Pushing characters...")
        if interaction.user.id == int(cfg.MAIN_ADMIN_ID):
            client.set_cookies(ltuid=cfg.genshin_data["ltuid"], ltoken=cfg.genshin_data["ltoken"])
            chars = await client.get_genshin_characters(cfg.genshin_data["uuid"])
            await pushCharacters(chars)
            await interaction.followup.send("Successfully pushed all characters to database", ephemeral=True)
    
    @app_commands.command(name="get_character", description="Get a character from the database")
    async def get_character(self, interaction, name: str):
        await interaction.response.defer()
        character = await getCharacter(name)
        if character:
            character = character.to_mongo()
            weapon = await getWeaponByObjId(character["weapon"])
            view = WeaponView(character, weapon)
            embed = genshinCharacterEmbed(character)
            await interaction.followup.send(embed=embed, view=view)
        else:
            await interaction.followup.send(f"Character called {name} not found", ephemeral=True)

    @app_commands.command(name="push_wishes", description="Push an excel file of all wishes to the database")
    async def getWishes(self, interaction, wishes_file:Attachment):
        await interaction.response.defer()
        if not wishes_file.filename.endswith(".xlsx"):
            await interaction.followup.send("Please upload a valid excel file")
            return
        filepath = './temp/wishes.xlsx'
        await wishes_file.save(filepath)
        try:
            if interaction.user.id == int(cfg.MAIN_ADMIN_ID):
                await push_all_wishes(filepath)
                await interaction.followup.send("Wishes pushed to database", ephemeral=True)
        except ValueError:
            await interaction.followup.send("Please upload a valid excel file")
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
