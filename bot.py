# discord.py
from inspect import trace
import discord
from discord.ext import commands
from discord.ui import Button, View

# Other modules
from json import JSONDecodeError
from traceback import format_exception
from datetime import datetime, timedelta
from typing import Literal
from datetime import timezone
import asyncio
import logging, logging.handlers, sys
# Dependency imports
from pytz import timezone as pytzTimezone
from datefinder import find_dates
import requests

# Custom imports
from database.management.connection import set_connections
from discord_tools.exceptions import OWException
from discord_tools.views.ps2_views import OWView
from discord_tools.tasks import updateGenshinChars
from utils.logger import define_log, StreamToLogger, exception_to_log
from utils.ps2 import continentToId
from utils.timezones import getIANA
from utils.exit_handlers import main_exit_handler
import config as cfg

# Discord Tools
from discord_tools.classes import AlertReminder
from discord_tools.data import alert_reminder_dict
from discord_tools.embeds import getOWRankings, getServerPanel, getCensusHealth, getOWEmbed, getOWMatchesData
from discord_tools.literals import Timezones
# Group commands
from command_groups.genshin_commands import GenshinDB

logging.getLogger('discord.http').setLevel(logging.INFO)
log = logging.getLogger('discord')

description = "A multipurpose bot made by ElReyZero"
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', description=description, intents=intents)

async def getAdmins()->list:
    """Simple function that retrieves the admin User objects from the discord api.

    Returns:
        List: List with the admin user objects
    """
    return [await bot.fetch_user(admin) for admin in cfg.admin_ids]

def setup_log():
    console_handler, file_handler, formatter = define_log()

    # Redirect stdout and stderr to log:
    sys.stdout = StreamToLogger(log, logging.INFO)
    sys.stderr = StreamToLogger(log, logging.ERROR)
    log.addHandler(file_handler)
    log.propagate = True
    discord.utils.setup_logging(handler=console_handler, formatter=formatter, level=logging.INFO)

@bot.event
async def on_ready():
    """ Modified function that runs on the 'on_ready' event from the bot, it syncs the commands and starts the bot
    """
    await bot.wait_until_ready()
    await bot.tree.sync()
    await bot.tree.sync(guild=discord.Object(id=cfg.MAIN_GUILD))
    await bot.change_presence(activity=discord.Game(name="with the API"))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    if cfg.connections:
        updateGenshinChars.start()

@bot.tree.error
async def on_app_command_error(interaction, error):
    """Modified function that runs on the 'on_app_command_error' event, it handles errors from the bot.
       The default behaviour is to send a warning to the user that triggered the command and DM the main admin regarding the exception (if debug is set to True).
    """
    # Depending on the type of exception, a different message will be sent
    traceback_message = format_exception(type(error), error, error.__traceback__)
    exception_to_log(log, traceback_message)
    try:
        original = error.original
    except AttributeError:
        original = error
    if type(original).__name__ == "ConnectionError":
        await interaction.response.send_message(f"{interaction.user.mention} The PS2 API timed out, please try again!")
        return
    elif type(original).__name__ == "403 Forbidden" or isinstance(original, discord.errors.Forbidden):
        await interaction.response.send_message(f"{interaction.user.mention} Your DM's are disabled.\nPlease enable 'Allow direct messages from server members' under the privacy tab of the server or 'Allow direct messages' on your privacy settings and try again.")
        return
    try:
        await interaction.response.send_message(("Uhhh something unexpected happened! Please try again or contact Rey if it keeps happening.\nDetails: *{}*").format(type(original).__name__))
    except discord.errors.InteractionResponded:
        try:
            await interaction.followup.send(("Uhhh something unexpected happened! Please try again or contact Rey if it keeps happening.\nDetails: *{}*").format(type(original).__name__))
        except discord.InteractionResponded:
            pass
    #If the DEBUG variable is set, the bot will DM the main admin with the whole traceback. It's meant for debug purposes only
    if cfg.DEBUG:
        user = await bot.fetch_user(cfg.MAIN_ADMIN_ID)
        try:
            try:
                traceback_message = "".join(format_exception(type(error), error, error.__traceback__))
                await user.send(f"Exception: {traceback_message}")
            except TypeError:
                etype, value, tb = sys.exc_info()
                traceback_message = "".join(format_exception(etype, value, tb))
                await user.send(f"Exception: {traceback_message}")
            except discord.errors.HTTPException:
                etype, value, tb = sys.exc_info()
                traceback_message = "".join(format_exception(etype, value, tb))
                await user.send(f"Exception: {traceback_message}")
                raise error
            raise error
        except discord.errors.HTTPException:
            pass

@commands.dm_only()
@bot.command(aliases=["logs", "getLogs"])
async def get_bot_logs(ctx):
    """Command that returns the bot log file to the user that requested it.
    """
    if ctx.author not in await getAdmins():
        await ctx.send("You don't have permission to use this command!")
        return
    try:
        await ctx.send("Here you go!", file=discord.File("./logs/bot.log"))
    except FileNotFoundError:
        await ctx.send("Here you go!", file=discord.File("/home/ReyBot/logs/bot.log"))

@bot.tree.command(name="alert_reminder", description="Set up a reminder before an alert ends!")
async def alertReminder(interaction: discord.Interaction, continent:Literal["Indar", "Amerish", "Hossin", "Esamir", "Oshur"], minutes:int=5):
    """Command that sets up a reminder before an alert ends.
    """
    # Check if the user had inputs for minutes, it also checks if it's valid
    minutes = 5 if minutes == None else minutes
    if minutes < 1:
        await interaction.response.send_message(f"{interaction.user.mention} Please enter a valid number of minutes.", ephemeral=True)
        return

    # Since the input is the continent name, it must be converted to it's census id
    cont_id = continentToId(continent)
    req = requests.get(f"https://api.ps2alerts.com/instances/active?world=17&zone={cont_id}")
    data = req.json()
    if len(data) > 0:
        data = data[0]
        # Formatting and replacing timezones
        startTime = data['timeStarted'][:-6]
        startTime = datetime.strptime(startTime, "%Y-%m-%dT%H:%M:%S")
        startTime = startTime.replace(tzinfo=timezone.utc).astimezone(tz=None)
        endTime = startTime + timedelta(minutes=90)

        if datetime.now() + timedelta(minutes=minutes) >= endTime.replace(tzinfo=None):
            await interaction.response.send_message(f"There is less than {minutes} minutes in the alert, you cannot set a reminder for that!")
            return

        # Setting up the alert reminder
        reminder = AlertReminder(continent, minutes, endTime, interaction.user)
        task = asyncio.create_task(reminder.checkRemainingReminderTime(interaction))
        reminder.setTask(task)
        # The bot will try to set the created reminder checking if there's one already set
        try:
            reminders = alert_reminder_dict[interaction.user.id]
            for reminder in reminders:
                if continent == reminder.continent:
                    await interaction.response.send_message(f"You've already set a reminder for {continent}", ephemeral=True)
                    return
            alert_reminder_dict[interaction.user.id].append(reminder)
        except KeyError:
            alert_reminder_dict[interaction.user.id] = list()
            alert_reminder_dict[interaction.user.id].append(reminder)
        await interaction.response.send_message(f"{interaction.user.mention} You have successfully set a reminder for {continent}\nThe alert will end <t:{int(endTime.timestamp())}:R>\nReminder set to {minutes} minutes before it ends")
        await task
    else:
        await interaction.response.send_message(f"{interaction.user.mention} There are no active alerts for {continent}", ephemeral=True)

@bot.tree.command(name="remove_alert_reminder", description="Remove an alert reminder")
async def removeReminder(interaction: discord.Interaction, continent:Literal["Indar", "Amerish", "Hossin", "Esamir", "Oshur"]):
    try:
        reminders = alert_reminder_dict[interaction.user.id]
        for reminder in reminders:
            if reminder.continent == continent:
                reminder.task.cancel()
                reminders.remove(reminder)
                await interaction.response.send_message(f"Your alert reminder for {continent} has been removed", ephemeral=True)
    except KeyError:
        await interaction.response.send_message(f"{interaction.user.mention} You do not have a reminder for {continent}", ephemeral=True)

@bot.tree.command(name="census_health", description="Get the census API health check")
async def censusHealth(interaction):
    try:
        embed = getCensusHealth()
    except JSONDecodeError:
        await interaction.response.send_message("Can't fetch data from Honu (It's most likely down). Please try again later.")
        return
    refresh = Button(label="Refresh", custom_id="refresh_health", style=discord.ButtonStyle.blurple)
    async def refreshCallback(interaction):
        await interaction.response.defer()
        try:
            embed = getCensusHealth()
            await interaction.edit_original_response(embed=embed)
        except discord.errors.NotFound:
            pass
        except JSONDecodeError:
            await interaction.followup.send("Can't fetch data from Honu (It's most likely down). Please try again later.")
            return
    refresh.callback = refreshCallback
    view = View(timeout=None)
    view.add_item(refresh)
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="check_personal_reminders", description="Check the alert reminders currently set (only for you)")
async def checkPersonalReminders(interaction):
    try:
        reminders = alert_reminder_dict[interaction.user.id]
        embed = discord.Embed(color=0xff0000, title=f"Alert Reminders for {str(interaction.user)}", description="Current alert reminders set")
        for reminder in reminders:
            embed.add_field(name=reminder.continent, value=f"{reminder.minutes} minutes before alert ends", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except KeyError:
        await interaction.response.send_message(f"{interaction.user.mention} You do not have any alert reminders set", ephemeral=True)

@bot.tree.command(name="global_alert_reminders", description="Check the alert reminders currently set (Debug)")
async def checkGlobalReminders(interaction):
    admins = await getAdmins()
    if interaction.user in admins:
        if len(alert_reminder_dict) > 0:
            embed = discord.Embed(color=0xff0000, title="Global Alert Reminders", description="Current alert reminders set within the bot")
            for user in alert_reminder_dict:
                username = alert_reminder_dict[user][0].user.name
                embed.add_field(name=username, value="᲼", inline=True)
                for reminder in alert_reminder_dict[user]:
                    embed.add_field(name=f'{reminder.continent}', value=f"{reminder.minutes} minutes before alert ends", inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(f"{interaction.user.mention} There are no alert reminders set", ephemeral=True)
    else:
        await interaction.response.send_message(f"{interaction.user.mention} You are not authorized to use this command", ephemeral=True)

@bot.tree.command(name="server_panel", description="Check the active alerts and open continents on a server. Default: Emerald")
async def checkServerPanel(interaction, server:Literal["Emerald", "Connery", "Cobalt", "Miller", "Soltech", "Jaeger"]="Emerald"):
    try:
        embed = getServerPanel(server)
        if embed:
            refresh = Button(label="Refresh", custom_id="refresh_alerts", style=discord.ButtonStyle.blurple)
            async def refreshCallback(interaction):
                await interaction.response.defer()
                try:
                    embed = getServerPanel(server)
                    await interaction.edit_original_response(embed=embed)
                except discord.errors.NotFound:
                    pass
                except JSONDecodeError:
                    await interaction.followup.send("Can't fetch data from Honu (It's most likely down). Please try again later.")
                    return
            refresh.callback = refreshCallback
            view = View(timeout=None)
            view.add_item(refresh)
            await interaction.response.send_message(embed=embed, view=view)
        else:
            await interaction.response.send_message(f"Can't fetch data from Honu (It's most likely down). Please try again later.")
    except JSONDecodeError:
        await interaction.followup.send("Can't fetch data from Honu (It's most likely down). Please try again later.")
        return


@bot.tree.command(name="send_timestamp", description="Send a timestamp for an event given a time, date and event name")
async def sendTimestamp(interaction, event_name:str, date:str, time:str, timezone:Timezones):
    await interaction.response.defer()
    try:
        date = find_dates(date)
        for dates in date:
            date = dates
            break
        time = time.split(":")
        timestamp = date.replace(hour=int(time[0]), minute=int(time[1]))
        timezone_py = pytzTimezone(getIANA(timezone))
        timestamp = timezone_py.localize(timestamp).astimezone(None)
        embed = discord.Embed(color=0x171717, title=f"{event_name}", description=f"{event_name} will happen at")
        embed.add_field(name="Date", value=f"<t:{int(timestamp.timestamp())}>", inline=True)
        embed.add_field(name="Relative", value=f"<t:{int(timestamp.timestamp())}:R>", inline=True)
        getTimestampsButton = Button(label="Get Timestamps", style=discord.ButtonStyle.blurple)
        ephemeral = False
        async def discordTimeFormatCallback(interaction):
            nonlocal ephemeral
            getTimestampsButton.disabled = True
            if ephemeral:
                await interaction.response.send_message(f"Date: \<t:{int(timestamp.timestamp())}>\nRelative: \<t:{int(timestamp.timestamp())}:R>", ephemeral=True)
            else:
                await interaction.response.send_message(f"Date: \<t:{int(timestamp.timestamp())}>\nRelative: \<t:{int(timestamp.timestamp())}:R>")
                ephemeral = True

        getTimestampsButton.callback = discordTimeFormatCallback
        view = View(timeout=None)
        view.add_item(getTimestampsButton)
        await interaction.followup.send(embed=embed, view=view)
    except AttributeError:
        await interaction.followup.send(f"{interaction.user.mention} Invalid date format", ephemeral=True)
    except (IndexError, ValueError):
        await interaction.followup.send(f"{interaction.user.mention} Invalid time format, time must be in the format HH:MM (24h)", ephemeral=True)

@bot.tree.command(name="get_ow_matches", description="Get the Outfit Wars matches for the current round")
async def getOWMatches(interaction, server:Literal["Emerald", "Connery", "Cobalt", "Miller", "Soltech"]="Emerald"):
    await interaction.response.defer()
    try:
        matches = getOWMatchesData(server)
    except OWException:
        await interaction.followup.send("Outfit Wars is Over!")
        return
    if len(matches) > 5:
        half = len(matches)//2
        pages = [matches[:half], matches[half:]]
        current_page = 1
        view = OWView(matches, server, match=True)
        embed = getOWEmbed(pages[current_page-1], server, current_page, len(pages))
        await interaction.followup.send(embed=embed, view=view)
    else:
        embed = getOWEmbed(matches, server, 1, 1)
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="get_ow_standings", description="Get the Outfit Wars standings for the current round")
async def getOWStandings(interaction, server:Literal["Emerald", "Connery", "Cobalt", "Miller", "Soltech"]="Emerald"):
    await interaction.response.defer()
    standings = getOWRankings(server)
    view = OWView(standings, server)
    current_page = 1
    pages = [standings]
    if len(standings) > 5:
        half = len(standings)//2
        pages = [standings[:half], standings[half:]]
        current_page = 1

    embed = getOWEmbed(pages[current_page-1], server, current_page, len(pages), match=False)
    await interaction.followup.send(embed=embed, view=view)

if __name__ == "__main__":
    # Defining the logger
    console_handler = setup_log()
    # Setting up the config
    cfg.get_config()
    cfg.connections = set_connections()
    if cfg.connections:
        main_exit_handler(cfg.connections)
        cfg.connections.connect("genshin")
    # Starting the bot
    bot.tree.add_command(GenshinDB(), guild=discord.Object(id=cfg.MAIN_GUILD))
    bot.run(cfg.DISCORD_TOKEN, log_handler=console_handler)