from deprecated import deprecated
from typing import Literal
from discord_tools.exceptions import OWException
from discord_tools.embeds import get_ow_embed, get_ow_matches_data, get_ow_rankings
from discord_tools.views.ps2_views import OWView
from discord.ext import commands
import discord
import asyncio

description = "A multipurpose bot made by ElReyZero"
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', description=description, intents=intents)

@bot.tree.command(name="ow_matches", description="Get the Outfit Wars matches for the current round")
async def get_ow_matches(interaction, server:Literal["Emerald", "Connery", "Cobalt", "Miller", "Soltech"]="Emerald"):
    await interaction.response.defer()
    try:
        matches = get_ow_matches_data(server)
    except OWException:
        await interaction.followup.send("Outfit Wars is Over!")
        return
    if len(matches) > 5:
        half = len(matches)//2
        pages = [matches[:half], matches[half:]]
        current_page = 1
        view = OWView(matches, server, match=True)
        embed = get_ow_embed(pages[current_page-1], server, current_page, len(pages))
        await interaction.followup.send(embed=embed, view=view)
    else:
        embed = get_ow_embed(matches, server, 1, 1)
        await interaction.followup.send(embed=embed)

@deprecated(version="0.0.1", reason="Outfit Wars is over")
@bot.tree.command(name="ow_standings", description="Get the Outfit Wars standings for the current round")
async def get_ow_standings(interaction, server:Literal["Emerald", "Connery", "Cobalt", "Miller", "Soltech"]="Emerald"):
    await interaction.response.defer()
    standings = get_ow_rankings(server)
    view = OWView(standings, server)
    current_page = 1
    pages = [standings]
    if len(standings) > 5:
        half = len(standings)//2
        pages = [standings[:half], standings[half:]]
        current_page = 1

    embed = get_ow_embed(pages[current_page-1], server, current_page, len(pages), match=False)
    await interaction.followup.send(embed=embed, view=view)