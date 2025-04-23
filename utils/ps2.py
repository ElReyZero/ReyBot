# pylint: disable=invalid-name, consider-using-dict-items
from dataclasses import dataclass
import requests

CONTINENT_IDS = {
    "Amerish": 6,
    "Esamir": 8,
    "Indar": 2,
    "Hossin": 4,
    "Oshur": 344,
}

SERVER_IDS = {
    1: "Osprey",
    3: "Helios",
    10: "Wainwright",
    13: "Cobalt",
    17: "Emerald",
    19: "Jaeger",
    24: "Apex",
    25: "Briggs",
    40: "Soltech",
    1000: "Genudine",
    2000: "Ceres"
}

CONTINENT_STATES = {
    0: "Locked",
    1: "Unstable (Single Lane)",
    2: "Unstable (Double Lane)",
    3: "Fully Open",
}

CLASS_IDS = {
    1: "Infiltrator",
    3: "Light Assault",
    4: "Medic",
    5: "Engineer",
    6: "Heavy Assault",
    7: "Max",
}


def continent_to_id(continent: str) -> int | None:
    for key in CONTINENT_IDS:
        if continent.capitalize() == key:
            return CONTINENT_IDS[key]
    return None


def id_to_continent_name(cont_id: int) -> str | None:
    for key in CONTINENT_IDS:
        if cont_id == CONTINENT_IDS[key]:
            return key
    return None


def server_id_to_name(server_id: int, active_server=True) -> str:
    if active_server:
        for key in SERVER_IDS:
            if server_id == key and key not in [3, 24, 25, 1000, 2000]:
                return SERVER_IDS[key]
    else:
        for key in SERVER_IDS:
            if server_id == key:
                return SERVER_IDS[key]
    return None


def name_to_server_id(name: str, active_server=True) -> int | None:
    if active_server:
        for key in SERVER_IDS:
            if name.capitalize() == SERVER_IDS[key] and key not in [3, 24, 25, 1000, 2000]:
                return key
    else:
        for key in SERVER_IDS:
            if name.capitalize() == SERVER_IDS[key]:
                return key
    return None



def id_to_continent_state(state_id) -> str | None:
    for key in CONTINENT_STATES:
        if state_id == key:
            return CONTINENT_STATES[key]
    return None


@dataclass
class CharacterStats:
    id: int
    battle_rank: int
    prestige_level: int
    raw_stats: list[dict]
    certs: int = None
    deaths: int = None
    kills: int = None
    kd: int = None
    kpm: int = None
    facility_captures: int = None
    facility_defenses: int = None
    score: int = None
    time: int = None

    def __post_init__(self):
        for stat in self.raw_stats:
            self._setAttr(stat["stat_name"], stat["all_time"])

    def _setAttr(self, attr: int, value: int):
        value = int(value)
        if attr == "battle_rank":
            self.battle_rank = value
        elif attr == "prestige_level":
            self.prestige_level = value
        elif attr == "certs":
            self.certs = value
        elif attr == "deaths":
            self.deaths = value
        elif attr == "kills":
            self.kills = value
        elif attr == "facility_capture":
            self.facility_captures = value
        elif attr == "facility_defend":
            self.facility_defenses = value
        elif attr == "score":
            self.score = value
        elif attr == "time":
            self.time = value

        if self.kills and self.deaths:
            self.kd = round(self.kills / self.deaths, 2)

        if self.kills and self.time:
            self.kpm = round(self.kills / (self.time / 60), 3)
