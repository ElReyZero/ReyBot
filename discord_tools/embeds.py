from json import JSONDecodeError
from operator import indexOf
import requests
from discord import Embed
from discord_tools.exceptions import OWException
from discord_tools.literals import ElementColor, ElementEmote
from datetime import datetime, timedelta, timezone
from utils.ps2 import nameToServerID, idToContinentName, serverIDToName, idToContinentState

def getServerPanel(server):
    id = nameToServerID(server)
    try:
        request = requests.get("https://wt.honu.pw/api/world/overview")
        data_pop = requests.get(f"https://wt.honu.pw/api/population/{id}").json()
        alertData = requests.get(f"https://api.ps2alerts.com/instances/active?world={id}").json()
        data = request.json()
        world_data = None
        embed = Embed(color=0x171717, title=f"{server} Panel", description=f"Current status and population of {server}", timestamp=datetime.now())
        if data:
            for world in data:
                if world["worldName"] == server:
                    world_data = world
                    break
            if world_data:
                for continent in world_data["zones"]:
                    cont_name = idToContinentName(continent["zoneID"])
                    totalControl = continent["territoryControl"]["total"]
                    if totalControl == continent['territoryControl']['vs'] or totalControl == continent['territoryControl']['nc'] or totalControl == continent['territoryControl']['tr']:
                        continue
                    territory=f"<:VS:1014970179291205745> VS: {int((continent['territoryControl']['vs']/totalControl)*100)}%\n"
                    territory += f"<:NC:1014970942235099177> NC: {int((continent['territoryControl']['nc']/totalControl)*100)}%\n"
                    territory += f"<:TR:1014970962493575262> TR: {int((continent['territoryControl']['tr']/totalControl)*100)}%"

                    if continent["alertStart"] and continent["isOpened"]:
                        for alert in alertData:
                            alertID = ""
                            if continent["zoneID"] == alert["zone"]:
                                alertID = alert["instanceId"]
                                break
                        startTime = datetime.strptime(continent["alertStart"][:-1], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).astimezone(tz=None)
                        try:
                            endTime = datetime.strptime(continent["alertEnd"][:-1], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).astimezone(tz=None)
                        except TypeError:
                            endTime = startTime + timedelta(minutes=90)
                        embed.add_field(name=cont_name, value=f"Alert in Progress:\n[Control territory to lock {cont_name}](https://ps2alerts.com/alert/{alertID})", inline=False)
                        embed.add_field(name="Start Time", value=f"<t:{int(startTime.timestamp())}:t>", inline=True)
                        embed.add_field(name="Time Left", value=f"Ends <t:{int(endTime.timestamp())}:R>", inline=True)
                        embed.add_field(name='\u200b', value='\u200b', inline=True)
                        embed.add_field(name="Territory Control", value=territory, inline=True)
                        population = f"Total: {continent['playerCount']}"
                        population += f"\n<:VS:1014970179291205745> VS: {continent['players']['vs']}"
                        population += f"\n<:NC:1014970942235099177> NC: {continent['players']['nc']}"
                        population += f"\n<:TR:1014970962493575262> TR: {continent['players']['tr']}"
                        population += f"\n<:NSO:1014970981556703362> NS (Unknown): {continent['players']['unknown']}"
                        embed.add_field(name="Population (Continent)", value=population, inline=True)
                    elif continent["isOpened"]:
                        unstableStateID = continent["unstableState"]
                        unstableState = idToContinentState(unstableStateID)
                        continentStatus = ""
                        if not cont_name == "Oshur":
                            if "Unstable" in unstableState:
                                continentStatus+= f"<:unstable:1014970998803664896> {unstableState}"
                            else:
                                continentStatus+= f"{unstableState}"
                        else:
                            continentStatus+= f"Fully Open"

                        embed.add_field(name=cont_name, value=f"Continent Status: {continentStatus}\n", inline=False)
                        embed.add_field(name="Territory Control", value=territory, inline=True)
                        population = f"Total: {continent['playerCount']}"
                        population += f"\n<:VS:1014970179291205745> VS: {continent['players']['vs']}"
                        population += f"\n<:NC:1014970942235099177> NC: {continent['players']['nc']}"
                        population += f"\n<:TR:1014970962493575262> TR: {continent['players']['tr']}"
                        population += f"\n<:NSO:1014970981556703362> NS (Unknown): {continent['players']['unknown']}"
                        embed.add_field(name="Population (Continent)", value=population, inline=True)
            populationGlobal = f"Total: {data_pop.get('total')}"
            populationGlobal += f"\n<:VS:1014970179291205745> VS: {data_pop.get('vs')}"
            populationGlobal += f"\n<:NC:1014970942235099177> NC: {data_pop.get('nc')}"
            populationGlobal += f"\n<:TR:1014970962493575262> TR: {data_pop.get('tr')}"
            populationGlobal += f"\n<:NSO:1014970981556703362> NS: {data_pop.get('ns')}"
            embed.add_field(name="Population (Global)", value=populationGlobal, inline=False)
            embed.set_footer(text="Last updated")
            return embed
        else:
            return None
    except JSONDecodeError:
        return None


def getCensusHealth():
    request = requests.get("https://wt.honu.pw/api/health")
    data = request.json()
    embed = Embed(color=0xff0000, title="Census API Health Check", description="Current status of the Census API separated by server events", timestamp=datetime.now())
    if data:
        for entry in data["death"]:
            if entry.get('failureCount')>= 30:
                status = "Down"
            elif entry.get('failureCount') > 0 and entry.get('failureCount') < 30:
                status = "Possible Issues"
            else:
                status = "Ok"
            eventTime = datetime.strptime(entry.get('lastEvent')[:-1], "%Y-%m-%d %H:%M:%S")
            eventTime = eventTime.replace(tzinfo=timezone.utc).astimezone(tz=None)
            server_name = serverIDToName(entry.get('worldID'))
            embed.add_field(name=server_name,
                            value=f"Last Event: <t:{int(eventTime.timestamp())}:R>\nLast Event Date: {entry.get('lastEvent')[:-1]} UTC\nFailure Count: {entry.get('failureCount')}\nStatus: {status}",
                            inline=True)
    else:
        embed.add_field(name="Error", value="There was an error getting the census API health check. This bot uses Honu to check the API's health so it might be down!", inline=True)

    embed.set_footer(text="Last updated")
    return embed

def getOWMatchesData(server):
    server_id = nameToServerID(server)
    currentRound = requests.get(f"https://api.ps2alerts.com/outfit-wars/{server_id}/current-round").json()
    req = requests.get(f"https://api.ps2alerts.com/outfit-wars/rankings?world={server_id}&round={currentRound}")
    data = req.json()
    sorted_rankings = sorted(data, key=lambda score: score["rankingParameters"]["TotalScore"], reverse=True)
    factions = {1: "<:VS:1014970179291205745>", 2: "<:NC:1014970942235099177>", 3: "<:TR:1014970962493575262>"}
    matches = list()
    outfit_limit = None
    if currentRound == 5:
        outfit_limit = 8
    elif currentRound == 6:
        outfit_limit = 4
    elif currentRound == 7:
        outfit_limit = 2
    elif currentRound >=7:
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
            winnerFaction = factions[instance["outfitwars"]["teams"][winner]["faction"]]
            winner_name = instance["outfitwars"]["teams"][winner]['name']
            matchString = f"{faction1}[{tag1}] {sorted_rankings[team1]['outfit']['name']} vs {faction2}[{tag2}] {sorted_rankings[team2]['outfit']['name']}\nWinner: {winnerFaction}[{winnerTag}] {winner_name}"
        matches.append(matchString)

    return matches


def getOWEmbed(data, server, current_page, pages, match=True):
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
        embed.add_field(name="Score (Wins + Points)", value=scores, inline=True)
    return embed

def getOWRankings(server):
    server_id = nameToServerID(server)
    req = requests.get(f"https://api.ps2alerts.com/outfit-wars/rankings?world={server_id}")
    data = req.json()
    current_round = data[0]["round"]
    sorted_rankings = sorted(data, key=lambda score: score["rankingParameters"]["TotalScore"], reverse=True)
    factions = {1: "<:VS:1014970179291205745>", 2: "<:NC:1014970942235099177>", 3: "<:TR:1014970962493575262>"}
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

def genshinCharacterEmbed(char_data):
    element_color = ElementColor[char_data['element']]
    element_emote = ElementEmote[char_data['element']]
    element = f"Element: {char_data['element']} {element_emote.value}\n"
    level = f"Level: {char_data['level']}\n"
    rarity = "Rarity: "+":star: " * char_data['rarity'] + "\n"
    friendship_lvl = f"Friendship Level <:friendship_lvl:1017420726992654356>: {char_data['friendship']}\n"
    constellation_lvl = f"Constellation Level: {char_data['constellation_level']}"
    desc = element + rarity + level + friendship_lvl + constellation_lvl
    embed = Embed(color=element_color.value, title=f"{char_data['name']}", description=desc)
    embed.set_image(url=char_data["icon"])

    return embed

def genshinWeaponEmbed(weapon_data):
    rarity = "Rarity: "+":star: " * weapon_data['rarity'] + "\n"
    level = f"Level: {weapon_data['level']}\n"
    type = f"Type: {weapon_data['type']}\n"
    refinement_lvl = f"Refinement Level: {weapon_data['refinement']}\n"
    desc = rarity + level + type + refinement_lvl
    embed = Embed(color=0x171717, title=f"{weapon_data['name']}", description=desc)
    embed.set_image(url=weapon_data["icon"])
    return embed