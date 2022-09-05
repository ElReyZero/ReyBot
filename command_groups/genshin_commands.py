from code import interact
from discord import app_commands, Attachment
import config as cfg
import genshin as gi
from database.populationScripts.genshin import pushCharacters, push_all_wishes
import os

class Genshin(app_commands.Group, name="genshin", description="Commands Related to Genshin Impact"):

    @app_commands.command(name="get_characters", description="Get all of your characters")
    async def get_characters(self, interaction, user_id: int):
        client = gi.Client()
        await interaction.response.send_message("Getting characters...")
        if interaction.user.id == int(cfg.MAIN_ADMIN_ID):
            client.set_cookies(ltuid=cfg.genshin_data["ltuid"], ltoken=cfg.genshin_data["ltoken"])
            chars = await client.get_genshin_characters(cfg.genshin_data["uuid"])
            await pushCharacters(chars)
        else:
            chars = await client.get_genshin_characters(user_id)
        await interaction.followup.send(f"Found {len(chars)} characters")
        await interaction.followup.send("Characters pushed to database", ephemeral=True)

    @app_commands.command(name="get_wishes", description="Get all of your wishes")
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