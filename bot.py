from json import JSONDecodeError
from traceback import format_exception
import os
import sys
from datetime import datetime, timedelta
from typing import Literal
import discord
from discord.app_commands import AppCommandError
from discord.ext import commands
from discord.ui import Button, View
import requests
from datetime import timezone
import asyncio
from pytz import timezone as pytzTimezone
from datefinder import find_dates
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from discord_tools.utils import continentToId
from discord_tools.classes import AlertReminder
from discord_tools.data import alert_reminder_dict, getIANATz
from discord_tools.functions import getServerPanel, getCensusHealth
from discord_tools.literals import Timezones
import config as cfg


description = "A bot for PlanetSide 2"
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', description=description, intents=intents)


async def getAdmins():
    return [await bot.fetch_user(admin) for admin in cfg.admin_ids]

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    await bot.tree.sync()
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"{ctx.author.mention} Invalid Command! Type `$help` for the list of available commands.")
    else:
        try:
            original = error.original
        except AttributeError:
            original = error
        if type(original).__name__ == "ConnectionError":
            await ctx.send(f"{ctx.author.mention} The PS2 API timed out, please try again!")
            return
        elif type(original).__name__ == "403 Forbidden" or isinstance(original, discord.errors.Forbidden):
            await ctx.send(f"{ctx.author.mention} Your DM's are disabled.\nPlease enable 'Allow direct messages from server members' under the privacy tab of the server or 'Allow direct messages' on your privacy settings and try again.")
            return
        await ctx.send(("Uhhh something unexpected happened! Please try again or contact Rey if it keeps happening.\nDetails: *{}*").format(type(original).__name__))
        user = await bot.fetch_user(cfg.main_admin_id)
        try:
            if not isinstance(original, discord.errors.Forbidden):
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

@bot.tree.error
async def on_error(interaction: discord.Interaction, error: AppCommandError):
    try:
        await interaction.response.send_message(("Uhhh something unexpected happened! Please try again or contact Rey if it keeps happening.\nDetails: *{}*").format(error))
    except discord.InteractionResponded:
        await interaction.followup.send(("Uhhh something unexpected happened! Please try again or contact Rey if it keeps happening.\nDetails: *{}*").format(error))

    traceback_message = "".join(format_exception(type(error), error, error.__traceback__))
    user = await bot.fetch_user(cfg.main_admin_id)
    await user.send(f"Exception: {traceback_message}")
    raise error


@bot.tree.command(name="alert_reminder", description="Set up a reminder before an alert ends!")
async def alertReminder(interaction: discord.Interaction, continent:Literal["Indar", "Amerish", "Hossin", "Esamir", "Oshur"], minutes:int=5):
    minutes = 5 if minutes == None else minutes
    if minutes < 1:
        await interaction.response.send_message(f"{interaction.user.mention} Please enter a valid number of minutes.", ephemeral=True)
        return

    cont_id = continentToId(continent)
    req = requests.get(f"https://api.ps2alerts.com/instances/active?world=17&zone={cont_id}")
    data = req.json()
    if len(data) > 0:
        data = data[0]
        startTime = data['timeStarted'][:-6]
        startTime = datetime.strptime(startTime, "%Y-%m-%dT%H:%M:%S")
        startTime = startTime.replace(tzinfo=timezone.utc).astimezone(tz=None)
        endTime = startTime + timedelta(minutes=90)

        if datetime.now() + timedelta(minutes=minutes) >= endTime.replace(tzinfo=None):
            await interaction.response.send_message(f"There is less than {minutes} minutes in the alert, you cannot set a reminder for that!")
            return

        reminder = AlertReminder(continent, minutes, endTime, interaction.user)
        task = asyncio.create_task(reminder.checkRemainingReminderTime(interaction))
        reminder.setTask(task)
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
            await interaction.edit_original_message(embed=embed)
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
                    await interaction.edit_original_message(embed=embed)
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


@bot.tree.command(name="send_timezone", description="Send a timezone for an event given a time and event name")
async def scheduleEvent(interaction, event_name:str, date:str, time:str, timezone:Timezones):
    await interaction.response.defer()
    try:
        date = find_dates(date)
        for dates in date:
            date = dates
            break
        time = time.split(":")
        timestamp = date.replace(hour=int(time[0]), minute=int(time[1]))
        timezone_py = pytzTimezone(getIANATz(timezone))
        timestamp = timezone_py.localize(timestamp).astimezone(None)
        embed = discord.Embed(color=0x171717, title=f"{event_name}", description=f"{event_name} will happen at")
        embed.add_field(name="Date", value=f"<t:{int(timestamp.timestamp())}>", inline=True)
        embed.add_field(name="Relative", value=f"<t:{int(timestamp.timestamp())}:R>", inline=True)
        await interaction.followup.send(embed=embed)
    except AttributeError:
        await interaction.followup.send(f"{interaction.user.mention} Invalid date format", ephemeral=True)
    except (IndexError, ValueError):
        await interaction.followup.send(f"{interaction.user.mention} Invalid time format, time must be in the format HH:MM (24h)", ephemeral=True)


if __name__ == "__main__":
    cfg.get_config()
    bot.run(cfg.DISCORD_TOKEN)