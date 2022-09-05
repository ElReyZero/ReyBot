import requests

CONTINENT_IDS = {
    "Amerish":6,
    "Esamir": 8,
    "Indar": 2,
    "Hossin": 4,
    "Oshur": 344,
    }

SERVER_IDS = {
    1:"Connery",
    3:"Helios",
    10:"Miller",
    13:"Cobalt",
    17:"Emerald",
    19:"Jaeger",
    24:"Apex",
    25:"Briggs",
    40:"Soltech",
    1000:"Genudine",
    2000:"Ceres"
}

CONTINENT_STATES = {
    0:"Locked",
    1:"Unstable (Single Lane)",
    2:"Unstable (Double Lane)",
    3:"Fully Open",
}

def continentToId(continent):
    for key in CONTINENT_IDS:
        if continent.capitalize() == key:
            return CONTINENT_IDS[key]
    return None

def idToContinentName(id):
    for key in CONTINENT_IDS:
        if id == CONTINENT_IDS[key]:
            return key
    return None

def serverIDToName(serverID, activeServer=True):
    if activeServer:
        for key in SERVER_IDS:
            if serverID == key and key not in [3,24,25,1000,2000]:
                return SERVER_IDS[key]
    else:
        for key in SERVER_IDS:
            if serverID == key:
                return SERVER_IDS[key]

def nameToServerID(name, activeServer=True):
    if activeServer:
        for key in SERVER_IDS:
            if name.capitalize() == SERVER_IDS[key] and key not in [3,24,25,1000,2000]:
                return key
    else:
        for key in SERVER_IDS:
            if name.capitalize() == SERVER_IDS[key]:
                return key
    return None

def checkEmeraldHealth():
    request = requests.get("https://wt.honu.pw/api/health")
    data = request.json()
    if data:
        for entry in data["death"]:
            if entry["worldID"] == 17 and entry['failureCount'] > 0:
                return False
            elif entry["worldID"] == 17:
                return True
    else:
        return None

def idToContinentState(id):
    for key in CONTINENT_STATES:
        if id == key:
            return CONTINENT_STATES[key]
    return None