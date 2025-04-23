# pylint: disable=anomalous-backslash-in-string,wrong-import-position
from utils.timezones import get_iana
from utils.ps2 import continent_to_id, name_to_server_id
from utils.logger import StreamToLogger, define_log, exception_to_log
from discord_tools.tasks import update_genshin_chars, update_server_panels
from discord_tools.modals import EventModal
from discord_tools.literals import Timezones
from discord_tools.embeds import (event_embed, get_census_health,
                                  get_ps2_character_embed)
from discord_tools.data import alert_reminder_dict, event_dict
from discord_tools.classes import AlertReminder
from command_groups.genshin_commands import GenshinDB
from command_groups.event_commands import SubscribeToEvents
import asyncio
import logging
import os
import signal
import sys
import time
from typing import Literal
from datetime import datetime, timedelta, timezone
from json import JSONDecodeError
from traceback import format_exception

import discord
from discord.errors import NotFound
from discord.ext import commands
from discord.ui import Button, View
import requests
import sentry_sdk
from datefinder import find_dates
from pytz import timezone as pytz_tz

# Setting up the config
import config as cfg
cfg.get_config()

logging.getLogger('discord.http').setLevel(logging.INFO)
log = logging.getLogger('ReyBot')

BOT_DESC = "A multipurpose bot made by ElReyZero"
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$',
                   description=BOT_DESC, intents=intents)


async def get_admins() -> list:
    """Simple function that retrieves the admin User objects from the discord api.

    Returns:
        List: List with the admin user objects
    """
    return [await bot.fetch_user(admin) for admin in cfg.admin_ids]


@bot.event
async def on_ready():
    """ Modified function that runs on the 'on_ready' event from the bot, it syncs the commands and starts the bot
    """
    await bot.wait_until_ready()
    await bot.tree.sync()
    await bot.tree.sync(guild=discord.Object(id=cfg.MAIN_GUILD))
    await bot.change_presence(activity=discord.Game(name="with the API"))
    cfg.bot_id = bot.user.id
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    if cfg.database["host"] != "":
        try:
            update_genshin_chars.start()
            update_server_panels.start(bot)
        except RuntimeError:
            pass


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: Exception):
    """Modified function that runs on the 'on_app_command_error' event, it handles errors from the bot.
       The default behaviour is to send a warning to the user that triggered the command and DM the main admin regarding the exception (if debug is set to True).
    """
    # Depending on the type of exception, a different message will be sent
    traceback_message = format_exception(type(error), error, error.__traceback__)
    exception_to_log(log, error)
    try:
        original = error.original
    except AttributeError:
        original = error
    if type(original).__name__ == "ConnectionError":
        await interaction.response.send_message(f"{interaction.user.mention} The PS2 API timed out, please try again!")
        return
    if type(original).__name__ == "403 Forbidden" or isinstance(original, discord.errors.Forbidden):
        message = f"{interaction.user.mention} Your DM's are disabled." \
            "Please enable 'Allow direct messages from server members' under the privacy tab of the server or 'Allow direct messages' on your privacy settings and try again."

        await interaction.response.send_message(message)
        return
    try:
        await interaction.response.send_message(f"Uhhh something unexpected happened! Please try again or contact Rey if it keeps happening.\nDetails: *{type(original).__name__}*")
    except discord.errors.InteractionResponded:
        pass
    if cfg.SENTRY_DSN:
        sentry_sdk.capture_exception(error)
    # If the DEBUG variable is set, the bot will DM the main admin with the whole traceback. It's meant for debug purposes only
    if cfg.DEBUG:
        user = await bot.fetch_user(cfg.MAIN_ADMIN_ID)
        try:
            try:
                traceback_message = "".join(format_exception(
                    type(error), error, error.__traceback__))
                await user.send(f"Exception: {traceback_message}")
            except TypeError:
                etype, value, tb = sys.exc_info()
                traceback_message = "".join(format_exception(etype, value, tb))
                await user.send(f"Exception: {traceback_message}")
            except discord.errors.HTTPException as e:
                etype, value, tb = sys.exc_info()
                traceback_message = "".join(format_exception(etype, value, tb))
                await user.send(f"Exception: {traceback_message}")
                raise error from e
            raise error
        except discord.errors.HTTPException:
            pass


@commands.dm_only()
@bot.command(aliases=["logs", "getLogs"])
async def get_bot_logs(ctx: commands.Context):
    """Command that returns the bot log file to the user that requested it.
    """
    if ctx.author not in await get_admins():
        await ctx.send("You don't have permission to use this command!")
        return
    try:
        await ctx.send("Here you go!", file=discord.File(cfg.PROJECT_PATH+"/logs/bot.log"))
    except FileNotFoundError:
        await ctx.send("The log file doesn't exist!")

# pylint: disable=line-too-long


@bot.tree.command(name="alert_reminder", description="Set up a reminder before an alert ends!")
async def alert_reminder(interaction: discord.Interaction, continent: Literal["Indar", "Amerish", "Hossin", "Esamir", "Oshur"], minutes: int = 5, server: Literal["Osprey", "Wainwright", "Soltech", "Jaeger", "Genudine", "Ceres"] = "Osprey"):
    """Command that sets up a reminder before an alert ends.
    """
    # Check if the user had inputs for minutes, it also checks if it's valid
    minutes = 5 if minutes is None else minutes
    if minutes < 1:
        await interaction.response.send_message(f"{interaction.user.mention} Please enter a valid number of minutes.", ephemeral=True)
        return

    # Since the input has the continent and server names, they must be converted to their respective census id
    cont_id = continent_to_id(continent)
    server_id = name_to_server_id(server, active_server=False)
    req = requests.get(f"https://api.ps2alerts.com/instances/active?world={server_id}&zone={cont_id}", timeout=90)
    data = req.json()
    if len(data) > 0:
        data = data[0]
        # Formatting and replacing timezones
        start_time = data['timeStarted'][:-6]
        start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
        start_time = start_time.replace(tzinfo=timezone.utc).astimezone(tz=None)
        end_time = start_time + timedelta(minutes=90)

        if datetime.now() + timedelta(minutes=minutes) >= end_time.replace(tzinfo=None):
            await interaction.response.send_message(f"There is less than {minutes} minutes in the alert, you cannot set a reminder for that!")
            return

        # Setting up the alert reminder
        reminder = AlertReminder(continent, minutes, end_time, interaction.user)
        reminder.schedule_reminder(interaction)
        try:
            reminders = alert_reminder_dict[interaction.user.id]
            for reminder in reminders:
                if continent == reminder.continent:
                    await interaction.response.send_message(f"You've already set a reminder for {continent}", ephemeral=True)
                    return
            alert_reminder_dict[interaction.user.id].append(reminder)
        except KeyError:
            alert_reminder_dict[interaction.user.id] = []
            alert_reminder_dict[interaction.user.id].append(reminder)
        await interaction.response.send_message(f"{interaction.user.mention} You have successfully set a reminder for {continent}\nThe alert will end <t:{int(end_time.timestamp())}:R>\nReminder set to {minutes} minutes before it ends")
    else:
        await interaction.response.send_message(f"{interaction.user.mention} There are no active alerts for {continent}", ephemeral=True)


@bot.tree.command(name="remove_alert_reminder", description="Remove an alert reminder")
async def remove_reminder(interaction: discord.Interaction, continent: Literal["Indar", "Amerish", "Hossin", "Esamir", "Oshur"]):
    try:
        reminders = alert_reminder_dict[interaction.user.id]
        for reminder in reminders:
            if reminder.continent == continent:
                reminder.scheduler.cancel(reminder.event)
                reminders.remove(reminder)
                await interaction.response.send_message(f"Your alert reminder for {continent} has been removed", ephemeral=True)
    except KeyError:
        await interaction.response.send_message(f"{interaction.user.mention} You do not have a reminder for {continent}", ephemeral=True)


@bot.tree.command(name="census_health", description="Get the census API health check")
async def census_health(interaction: discord.Interaction):
    try:
        embed = get_census_health()
    except JSONDecodeError:
        await interaction.response.send_message("Can't fetch data from Honu (It's most likely down). Please try again later.")
        return
    refresh = Button(label="Refresh", custom_id="refresh_health",
                     style=discord.ButtonStyle.blurple)

    async def refresh_callback(interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            embed = get_census_health()
            await interaction.edit_original_response(embed=embed)
        except discord.errors.NotFound:
            pass
        except JSONDecodeError:
            await interaction.followup.send("Can't fetch data from Honu (It's most likely down). Please try again later.")
            return
    refresh.callback = refresh_callback
    view = View(timeout=None)
    view.add_item(refresh)
    await interaction.response.send_message(embed=embed, view=view)


@bot.tree.command(name="check_personal_reminders", description="Check the alert reminders currently set (only for you)")
async def check_personal_reminders(interaction: discord.Interaction):
    try:
        reminders = alert_reminder_dict[interaction.user.id]
        embed = discord.Embed(
            color=0xff0000, title=f"Alert Reminders for {str(interaction.user)}", description="Current alert reminders set")
        for reminder in reminders:
            embed.add_field(name=reminder.continent,
                            value=f"{reminder.minutes} minutes before alert ends", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except KeyError:
        await interaction.response.send_message(f"{interaction.user.mention} You do not have any alert reminders set", ephemeral=True)

# pylint: disable=redefined-outer-name


@bot.tree.command(name="send_timestamp", description="Send a timestamp for an event given a time, date and event name")
async def send_timestamp(interaction: discord.Interaction, event_name: str, date: str, time: str, timezone: Timezones):
    await interaction.response.defer()
    try:
        date = find_dates(date)
        for dates in date:
            date = dates
            break
        time = time.split(":")
        timestamp = date.replace(hour=int(time[0]), minute=int(time[1]))
        timezone_py = pytz_tz(get_iana(timezone))
        timestamp = timezone_py.localize(timestamp).astimezone(None)
        embed = discord.Embed(
            color=0x171717, title=f"{event_name}", description=f"{event_name} will happen at")
        embed.add_field(
            name="Date", value=f"<t:{int(timestamp.timestamp())}>", inline=True)
        embed.add_field(
            name="Relative", value=f"<t:{int(timestamp.timestamp())}:R>", inline=True)
        get_timestamps_button = Button(
            label="Get Timestamps", style=discord.ButtonStyle.blurple)
        ephemeral = False

        async def discord_time_format_callback(interaction: discord.Interaction):
            nonlocal ephemeral
            get_timestamps_button.disabled = True
            if ephemeral:
                await interaction.response.send_message(fr"Date: \<t:{int(timestamp.timestamp())}>\nRelative: \<t:{int(timestamp.timestamp())}:R>", ephemeral=True)
            else:
                await interaction.response.send_message(fr"Date: \<t:{int(timestamp.timestamp())}>\nRelative: \<t:{int(timestamp.timestamp())}:R>")
                ephemeral = True

        get_timestamps_button.callback = discord_time_format_callback
        view = View(timeout=None)
        view.add_item(get_timestamps_button)
        await interaction.followup.send(embed=embed, view=view)
    except AttributeError:
        await interaction.followup.send(f"{interaction.user.mention} Invalid date format", ephemeral=True)
    except (IndexError, ValueError):
        await interaction.followup.send(f"{interaction.user.mention} Invalid time format, time must be in the format HH:MM (24h)", ephemeral=True)


@bot.tree.command(name="character", description="Get the stats of a character")
async def get_character_stats(interaction: discord.Interaction, character_name: str):
    await interaction.response.defer()
    embed = await get_ps2_character_embed(character_name)
    if embed:
        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send("Character not found")


@bot.tree.command(name="crear_evento", description="Crea un evento")
async def create_event(interaction: discord.Interaction, zona_horaria: Timezones = "EST"):
    await interaction.response.send_modal(EventModal(zona_horaria))


@bot.tree.command(name="agregar_jugador", description="Agrega un jugador a un evento")
async def add_player_to_event(interaction: discord.Interaction, id_evento: str, jugador: discord.Member):
    channel = interaction.channel
    try:
        if interaction.user.id != event_dict[id_evento].owner_id:
            await interaction.response.send_message("No puedes agregar jugadores ya que no eres dueño del evento", ephemeral=True)
            return
        message = await channel.fetch_message(event_dict[id_evento].message_id)
        if jugador.mention in event_dict[id_evento].accepted:
            await interaction.response.send_message(f"{jugador.mention} ya está en el evento", ephemeral=True)
            return
        if jugador.mention in event_dict[id_evento].reserves:
            event_dict[id_evento].reserves.remove(jugador.mention)

        if len(event_dict[id_evento].accepted) == event_dict[id_evento].player_count:
            event_dict[id_evento].reserves.append(jugador.mention)
        else:
            event_dict[id_evento].accepted.append(jugador.mention)
        evento = event_dict[id_evento]

        await message.edit(embed=event_embed(id_evento, evento.date, evento.time, evento.timezone, evento.activity, evento.description, evento.player_count, evento.accepted, evento.reserves))
        await interaction.response.send_message(f"{jugador.mention} fue agregado al evento {id_evento}", ephemeral=True)
    except KeyError:
        await interaction.response.send_message(f"{interaction.user.mention} No se encontró el evento {id_evento}", ephemeral=True)
        return
    except NotFound:
        await interaction.response.send_message(f"{interaction.user.mention} Solo puedes agregar jugadores en el canal donde se creó el evento", ephemeral=True)
        return


@bot.tree.command(name="remover_jugador", description="Remueve un jugador de un evento")
async def remove_player_from_event(interaction: discord.Interaction, id_evento: str, jugador: discord.Member):
    channel = interaction.channel
    try:
        if interaction.user.id != event_dict[id_evento].owner_id:
            await interaction.response.send_message("No puedes remover jugadores ya que no eres dueño del evento", ephemeral=True)
            return
        message = await channel.fetch_message(event_dict[id_evento].message_id)
        if jugador.mention in event_dict[id_evento].accepted:
            event_dict[id_evento].accepted.remove(jugador.mention)
        elif jugador.mention in event_dict[id_evento].reserves:
            event_dict[id_evento].reserves.remove(jugador.mention)
        else:
            await interaction.response.send_message(f"{jugador.mention} no está en el evento", ephemeral=True)
            return

        evento = event_dict[id_evento]

        await message.edit(embed=event_embed(id_evento, evento.date, evento.time, evento.timezone, evento.activity, evento.description, evento.player_count, evento.accepted, evento.reserves))
        await interaction.response.send_message(f"{jugador.mention} fue removido del evento {id_evento}", ephemeral=True)
    except KeyError:
        await interaction.response.send_message(f"{interaction.user.mention} No se encontró el evento {id_evento}", ephemeral=True)
        return
    except NotFound:
        await interaction.response.send_message(f"{interaction.user.mention} Solo puedes remover jugadores en el canal donde se creó el evento", ephemeral=True)
        return


@commands.dm_only()
@bot.tree.command(name="restart_bot", description="Restarts the bot manually. Admin only.")
async def restart_bot(interaction: discord.Interaction):
    def check(m):
        return (m.content.lower() == "y" or m.content.lower() == "n" or m.content.lower() == "yes" or m.content.lower() == "no")

    def restart():
        time.sleep(5)
        os.execv(sys.executable, ['python3'] + sys.argv)

    if str(interaction.user.id) not in cfg.admin_ids:
        log.info(f"{interaction.user.id} tried to restart the bot")
        await interaction.response.send_message("You don't have permission to use this command!")
        return

    try:
        await interaction.response.send_message("Are you sure you want to restart the bot? (yes/no)")
        msg = await bot.wait_for("message", check=check, timeout=60)
        if msg.content.lower() == "no" or msg.content.lower() == "n":
            await interaction.followup.send("Restart cancelled")
            return

        await interaction.followup.send("Restarting...")
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, restart)
        await exit_handler()
    except asyncio.TimeoutError:
        await interaction.followup.send("Restart cancelled due to timeout...")
        return


async def exit_handler():
    if cfg.SENTRY_DSN:
        sentry_sdk.flush()
        log.info("Sentry has been flushed")

    log.info("Shutting down bot...")
    await bot.close()
    log.info("Bot has been shut down")
    sys.exit(0)


def setup_log():
    console_handler, file_handler, formatter = define_log()
    # Redirect stdout and stderr to log:
    sys.stdout = StreamToLogger(log, logging.INFO)
    sys.stderr = StreamToLogger(log, logging.ERROR)
    log.addHandler(file_handler)
    log.propagate = True
    discord.utils.setup_logging(handler=console_handler, formatter=formatter, level=logging.INFO)


async def main():

    signal.signal(signal.SIGINT, lambda sig, frame: asyncio.create_task(exit_handler()))
    signal.signal(signal.SIGTERM, lambda sig, frame: asyncio.create_task(exit_handler()))

    setup_log()
    if cfg.SENTRY_DSN:
        sentry_sdk.init(dsn=cfg.SENTRY_DSN, enable_tracing=True, traces_sample_rate=1.0)

    async with bot:
        await bot.add_cog(SubscribeToEvents())
        await bot.add_cog(GenshinDB(), guild=discord.Object(id=cfg.MAIN_GUILD))
        await bot.start(cfg.DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
