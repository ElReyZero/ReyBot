from deprecated import deprecated
from discord_tools.data import alert_reminder_dict
from discord.ext import commands
import discord
import config as cfg

description = "A multipurpose bot made by ElReyZero"
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', description=description, intents=intents)

async def get_admins() -> list:
    """Simple function that retrieves the admin User objects from the discord api.

    Returns:
        List: List with the admin user objects
    """
    return [await bot.fetch_user(admin) for admin in cfg.admin_ids]

@deprecated(version="0.0.2", reason="Unused command")
@bot.tree.command(name="global_alert_reminders", description="Check the alert reminders currently set (Debug)")
async def check_global_reminders(interaction: discord.Interaction):
    admins = await get_admins()
    if interaction.user in admins:
        if len(alert_reminder_dict) > 0:
            embed = discord.Embed(color=0xff0000, title="Global Alert Reminders",
                                  description="Current alert reminders set within the bot")
            for user in alert_reminder_dict:
                username = alert_reminder_dict[user][0].user.name
                embed.add_field(name=username, value="᲼", inline=True)
                for reminder in alert_reminder_dict[user]:
                    embed.add_field(
                        name=f'{reminder.continent}', value=f"{reminder.minutes} minutes before alert ends", inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(f"{interaction.user.mention} There are no alert reminders set", ephemeral=True)
    else:
        await interaction.response.send_message(f"{interaction.user.mention} You are not authorized to use this command", ephemeral=True)