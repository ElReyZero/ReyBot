from datetime import datetime, timedelta, timezone
from json import JSONDecodeError
from operator import indexOf
from typing import Optional

import auraxium
import requests
from auraxium import ps2
from datefinder import find_dates
from deprecated import deprecated
from discord import Embed
from pytz import timezone as pytz_tz

import config as cfg
from discord_tools.exceptions import OWException
from discord_tools.literals import ElementColor, ElementEmote
from utils.ps2 import (CharacterStats, id_to_continent_name,
                       id_to_continent_state, name_to_server_ID,
                       server_id_to_name)
from utils.timezones import get_IANA


def get_server_panel(server: str, is_subscription=False) -> Optional[Embed]:
    def get_continent_territory_control(continent):
        total_control = continent['territoryControl']['total']
        vs_percentage = int((continent['territoryControl']['vs'] / total_control) * 100)
        nc_percentage = int((continent['territoryControl']['nc'] / total_control) * 100)
        tr_percentage = int((continent['territoryControl']['tr'] / total_control) * 100)
        return f"<:VS:1014970179291205745> VS: {vs_percentage}%\n" \
               f"<:NC:1014970942235099177> NC: {nc_percentage}%\n" \
               f"<:TR:1014970962493575262> TR: {tr_percentage}%"

    def get_continent_population(continent):
        total_players = continent['playerCount']
        if total_players == 0:
            return "No players"
        vs_percentage = round(continent['players']['vs'] / total_players * 100, 2)
        nc_percentage = round(continent['players']['nc'] / total_players * 100, 2)
        tr_percentage = round(continent['players']['tr'] / total_players * 100, 2)
        unknown_percentage = round(continent['players']['unknown'] / total_players * 100, 2)
        return f"Total: {total_players}\n" \
               f"<:VS:1014970179291205745> VS: {vs_percentage}%\n" \
               f"<:NC:1014970942235099177> NC: {nc_percentage}%\n" \
               f"<:TR:1014970962493575262> TR: {tr_percentage}%\n" \
               f"<:NSO:1014970981556703362> NS (Unknown): {unknown_percentage}%"

    try:
        id = name_to_server_ID(server, activeServer=False)
        request = requests.get("https://wt.honu.pw/api/world/overview", timeout=5)
        data_pop = requests.get(f"https://wt.honu.pw/api/population/{id}", timeout=5).json()
        alert_data = requests.get(f"https://api.ps2alerts.com/instances/active?world={id}", timeout=5).json()
        data = request.json()

        if data:
            for world in data:
                if world["worldName"] == server:
                    world_data = world
                    break
            else:
                return None

            embed = Embed(color=0x171717, title=f"{server} Panel",
                          description=f"Current status and population of {server}", timestamp=datetime.now())

            for continent in world_data["zones"]:
                cont_name = id_to_continent_name(continent["zoneID"])
                territory = get_continent_territory_control(continent)
                population = get_continent_population(continent)

                if continent["alertStart"] and continent["isOpened"]:
                    for alert in alert_data:
                        if continent["zoneID"] == alert["zone"]:
                            alert_id = alert["instanceId"]
                            break
                    else:
                        alert_id = ""

                    start_time = datetime.strptime(continent["alertStart"][:-1], "%Y-%m-%dT%H:%M:%S") \
                        .replace(tzinfo=timezone.utc).astimezone(tz=None)
                    end_time = datetime.strptime(continent["alertEnd"][:-1], "%Y-%m-%dT%H:%M:%S") \
                        .replace(tzinfo=timezone.utc).astimezone(tz=None) if continent["alertEnd"] else start_time + timedelta(minutes=90)

                    embed.add_field(name=cont_name,
                                    value=f"Alert in Progress:\n[Control territory to lock {cont_name}](https://ps2alerts.com/alert/{alert_id})",
                                    inline=False)
                    embed.add_field(name="Start Time", value=f"<t:{int(start_time.timestamp())}:t>", inline=True)
                    embed.add_field(name="Time Left", value=f"Ends <t:{int(end_time.timestamp())}:R>", inline=True)
                    embed.add_field(name='\u200b', value='\u200b', inline=True)
                    embed.add_field(name="Territory Control", value=territory, inline=True)
                    embed.add_field(name="Population (Continent)", value=population, inline=True)

                elif continent["isOpened"]:
                    unstable_state_id = continent["unstableState"]
                    unstable_state = id_to_continent_state(unstable_state_id)
                    continent_status = f"Continent Status: <:unstable:1014970998803664896> {unstable_state}\n" if unstable_state and not cont_name == "Oshur" else "Fully Open"
                    embed.add_field(name=cont_name, value=continent_status, inline=False)
                    embed.add_field(name="Territory Control", value=territory, inline=True)
                    embed.add_field(name="Population (Continent)", value=population, inline=True)
            if data_pop.get('total') == 0:
                population_global = "Total: No players, either the server is deserted or in maintenance"
            else:
                population_global = f"Total: {data_pop.get('total')}\n" \
                                    f"<:VS:1014970179291205745> VS: {round(data_pop.get('vs') / data_pop.get('total') * 100, 2)}%\n" \
                                    f"<:NC:1014970942235099177> NC: {round(data_pop.get('nc') / data_pop.get('total') * 100, 2)}%\n" \
                                    f"<:TR:1014970962493575262> TR: {round(data_pop.get('tr') / data_pop.get('total') * 100, 2)}%\n" \
                                    f"<:NSO:1014970981556703362> NS: {round(data_pop.get('ns') / data_pop.get('total') * 100, 2)}%"
            embed.add_field(name="Population (Global)", value=population_global, inline=False)
            if is_subscription:
                embed.set_footer(text="Updates every 5 minutes - Last updated")
            else:
                embed.set_footer(text="Last updated")
            return embed
        else:
            return None

    except (JSONDecodeError, requests.Timeout):
        return None


def get_census_health() -> Optional[Embed]:
    try:
        request = requests.get("https://wt.honu.pw/api/health")
        data = request.json()
        embed = Embed(color=0xff0000, title="Census API Health Check",
                      description="Current status of the Census API separated by server events", timestamp=datetime.now())

        if data:
            for entry in data.get("death", []):
                failure_count = entry.get('failureCount')
                status = "Down" if failure_count >= 30 else "Possible Issues" if failure_count > 0 else "Ok"
                event_time = datetime.strptime(entry.get('lastEvent')[:-1], "%Y-%m-%dT%H:%M:%S") \
                    .replace(tzinfo=timezone.utc).astimezone(tz=None)
                server_name = server_id_to_name(entry.get('worldID'), activeServer=False)
                embed.add_field(name=server_name,
                                value=f"Last Event: <t:{int(event_time.timestamp())}:R>\n"
                                      f"Last Event Date: {entry.get('lastEvent')[:-1]} UTC\n"
                                      f"Failure Count: {failure_count}\nStatus: {status}",
                                inline=True)
        else:
            embed = Embed(color=0xff0000, title="Census API Health Check",
                          description="Error retrieving data from the Census API health check.",
                          timestamp=datetime.now())
            embed.add_field(name="Error", value="There was an error getting the census API health check. This bot uses Honu to check the API's health so it might be down!", inline=True)
    except requests.RequestException:
        embed = Embed(color=0xff0000, title="Census API Health Check",
                      description="Error retrieving data from the Census API health check.",
                      timestamp=datetime.now())
        embed.add_field(name="Error", value="There was an error getting the census API health check. This bot uses Honu to check the API's health so it might be down!", inline=True)

    embed.set_footer(text="Last updated")
    return embed


@deprecated(version="0.0.1", reason="Reason: Outfit Wars is over")
def get_ow_matches_data(server: str) -> Embed:
    server_id = name_to_server_ID(server)
    currentRound = requests.get(f"https://api.ps2alerts.com/outfit-wars/{server_id}/current-round").json()
    req = requests.get(f"https://api.ps2alerts.com/outfit-wars/rankings?world={server_id}&round={currentRound}")
    data = req.json()
    sorted_rankings = sorted(
        data, key=lambda score: score["rankingParameters"]["TotalScore"], reverse=True)
    factions = {1: "<:VS:1014970179291205745>",
                2: "<:NC:1014970942235099177>", 3: "<:TR:1014970962493575262>"}
    matches = list()
    outfit_limit = None
    if currentRound == 5:
        outfit_limit = 8
    elif currentRound == 6:
        outfit_limit = 4
    elif currentRound == 7:
        outfit_limit = 4
    elif currentRound >= 7:
        raise OWException()

    if outfit_limit:
        sorted_rankings = sorted_rankings[:outfit_limit]
    for i in range(0, len(sorted_rankings)-1, 2):
        startTime = datetime.strptime(sorted_rankings[i]['startTime'][:-5], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc).astimezone(tz=None)
        if outfit_limit:
            team1 = i
            team2 = len(sorted_rankings)-i-1
        else:
            team1 = i
            team2 = i+1
        faction1 = factions[sorted_rankings[team1]['outfit']['faction']]
        faction2 = factions[sorted_rankings[team2]['outfit']['faction']]
        tag1 = sorted_rankings[team1]['outfit']['tag']
        tag2 = sorted_rankings[team2]['outfit']['tag']
        if not sorted_rankings[team1]["instanceId"]:
            matchString = f"{faction1}[{tag1}] {sorted_rankings[team1]['outfit']['name']} vs {faction2}[{tag2}] {sorted_rankings[team2]['outfit']['name']}\nStart Time: <t:{int(startTime.timestamp())}>"
        else:
            instance = requests.get(f"https://api.ps2alerts.com/outfit-wars/{sorted_rankings[team1]['instanceId']}").json()
            winner = "blue" if instance["result"]["blue"] > instance["result"]["red"] else "red"
            winnerTag = instance["outfitwars"]["teams"][winner]["tag"]
            winnerFaction = factions[instance["outfitwars"]
                                     ["teams"][winner]["faction"]]
            winner_name = instance["outfitwars"]["teams"][winner]['name']
            matchString = f"{faction1}[{tag1}] {sorted_rankings[team1]['outfit']['name']} vs {faction2}[{tag2}] {sorted_rankings[team2]['outfit']['name']}\nWinner: {winnerFaction}[{winnerTag}] {winner_name}"
        matches.append(matchString)

    return matches


@deprecated(version="0.0.1", reason="Reason: Outfit Wars is over")
def get_ow_embed(data: list, server: str, current_page: int, pages: int, match=True) -> Embed:
    if match:
        embed = Embed(color=0x171717, title=f"Outfit Wars Matches for {server}", description=f"Page {current_page}/{pages}")
        for match in data:
            embed.add_field(name=f"Match {indexOf(data, match) +1}", value=match, inline=False)
    else:
        embed = Embed(color=0x171717, title=f"Outfit Wars Rankings for {server}", description=f"Page {current_page}/{pages}")
        positions = ""
        names = ""
        scores = ""
        for entry in data:
            positions += f"{entry[0]}\n"
            names += f"{entry[1]}\n"
            scores += f"{entry[2]}\n"
        embed.add_field(name="Rank", value=positions, inline=True)
        embed.add_field(name="Outfit Name", value=names, inline=True)
        embed.add_field(name="Score (Wins + Points)",
                        value=scores, inline=True)
    return embed


@deprecated(version="0.0.1", reason="Reason: Outfit Wars is over")
def get_ow_rankings(server: str) -> list:
    server_id = name_to_server_ID(server)
    req = requests.get(
        f"https://api.ps2alerts.com/outfit-wars/rankings?world={server_id}")
    data = req.json()
    current_round = data[0]["round"]
    sorted_rankings = sorted(
        data, key=lambda score: score["rankingParameters"]["TotalScore"], reverse=True)
    factions = {1: "<:VS:1014970179291205745>",
                2: "<:NC:1014970942235099177>", 3: "<:TR:1014970962493575262>"}
    rankings = list()
    counter = 1
    for i in range(len(sorted_rankings)):
        if sorted_rankings[i]["round"] == current_round:
            faction = factions[sorted_rankings[i]['outfit']['faction']]
            tag = sorted_rankings[i]['outfit']['tag']
            name = sorted_rankings[i]['outfit']['name']
            score = sorted_rankings[i]['rankingParameters']['TotalScore']
            rankings.append([f"{counter}.", f"{faction}[{tag}] {name}", score])
            counter += 1
    return rankings


async def get_PS2_character_embed(char_name: str) -> Optional[Embed]:
    async with auraxium.Client(service_id=cfg.SERVICE_ID) as client:
        char = await client.get_by_name(ps2.Character, char_name)
        if not char:
            return None

        server = await char.world()
        faction = await char.faction()
        stats = await char.stat_history(results=100)
        outfit = await char.outfit()
        title = await char.title()

        factions = {1: "<:VS:1014970179291205745>", 2: "<:NC:1014970942235099177>",
                    3: "<:TR:1014970962493575262>", 4: "<:NSO:1014970962493575262>"}
        faction_colors = {1: 0x5400ca, 2: 0x2986cc, 3: 0xFF0000, 4: 0x999999}

        char_stats = CharacterStats(char.id, char.battle_rank, char.data.prestige_level, stats)

        embed = Embed(color=faction_colors[faction.id], title=f"{char.name}\nLink: https://wt.honu.pw/c/{char.id}",
                      description=f"{title if title else 'Player'} of the {server} {faction.name}")

        embed.add_field(name="Server", value=server, inline=True)
        embed.add_field(name="Faction", value=factions[faction.id] + " " + faction.name.en, inline=True)
        embed.add_field(name="Battle Rank", value=char.battle_rank.value, inline=True)
        embed.add_field(name="ASP", value=char.data.prestige_level, inline=True)
        embed.add_field(name="Last Login", value=f"<t:{int(char.times.last_login)}:R>", inline=True)
        embed.add_field(name="Is Online", value="Yes" if await char.is_online() else "No", inline=True)
        embed.add_field(name="Kills", value=char_stats.kills, inline=True)
        embed.add_field(name="Overall KD", value=char_stats.KD, inline=True)
        embed.add_field(name="Overall KPM", value=char_stats.KPM, inline=True)
        embed.add_field(name="Outfit", value=f"[[{outfit.tag}] {outfit.name}](https://wt.honu.pw/o/{outfit.id}) ", inline=True)

        return embed


def genshin_character_embed(char_data: dict) -> Embed:
    element_color = ElementColor[char_data.element]
    element_emote = ElementEmote[char_data.element]
    element = f"Element: {char_data.element} {element_emote.value}\n"
    level = f"Level: {char_data.level}\n"
    rarity = "Rarity: "+":star: " * char_data.rarity + "\n"
    friendship_lvl = f"Friendship Level <:friendship_lvl:1017420726992654356>: {char_data.friendship}\n"
    constellation_lvl = f"Constellation Level: {char_data.constellation_level}"
    desc = element + rarity + level + friendship_lvl + constellation_lvl
    embed = Embed(color=element_color.value, title=f"{char_data.name}", description=desc)
    embed.set_image(url=char_data.icon)

    return embed


def genshin_weapon_embed(weapon_data: dict) -> Embed:
    rarity = "Rarity: "+":star: " * weapon_data['rarity'] + "\n"
    level = f"Level: {weapon_data['level']}\n"
    type = f"Type: {weapon_data['type']}\n"
    refinement_lvl = f"Refinement Level: {weapon_data['refinement']}\n"
    desc = rarity + level + type + refinement_lvl
    embed = Embed(color=0x171717,
                  title=f"{weapon_data['name']}", description=desc)
    embed.set_image(url=weapon_data["icon"])
    return embed


def event_embed(event_id, date, time, datetime, activity, description, player_count, accepted=[], reserves=[]):
    date = find_dates(date, first="day")
    for dates in date:
        date = dates
        break
    time = time.split(":")
    timestamp = date.replace(hour=int(time[0]), minute=int(time[1]))
    timezone_py = pytz_tz(get_IANA(datetime))
    timestamp = timezone_py.localize(timestamp).astimezone(None)

    accepted_text = ""
    reserves_text = ""

    for i in accepted:
        accepted_text += f"{i}\n"

    for i in reserves:
        reserves_text += f"{i}\n"

    embed = Embed(
        color=0xFFD200, title=f"Actividad: {activity}")
    embed.add_field(name="Id del evento", value=event_id, inline=False)
    embed.add_field(name="Descripción", value=description, inline=False)
    embed.add_field(
        name="Hora de inicio", value=f"<t:{int(timestamp.timestamp())}>", inline=False)
    embed.add_field(
        name="Empieza:", value=f"<t:{int(timestamp.timestamp())}:R>", inline=False)
    embed.add_field(name=f":white_check_mark: Escuadra ({len(accepted)}/{player_count})", value= "           -" if len(accepted) == 0 else accepted_text, inline=True)
    embed.add_field(name=":question: Reservas", value="           -" if len(reserves) == 0 else reserves_text, inline=True)

    return embed