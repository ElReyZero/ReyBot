from typing import Literal
from enum import Enum

class Months(Enum):
    January = 1
    February = 2
    March = 3
    April = 4
    May = 5
    June = 6
    July = 7
    August = 8
    September = 9
    October = 10
    November = 11
    December = 12

Years = Literal[2022, 2023]
Timezones = Literal['AST', 'CDT', 'CST', 'EDT', 'EST', 'MDT', 'MST', 'PDT', 'PST','UTC']

class ElementColor(Enum):
    Anemo = 0x77e6c3
    Cryo = 0xa0e9e5
    Dendro = 0xbeff6e
    Electro = 0xa757cb
    Geo = 0xe3b342
    Hydro = 0x21e1eb
    Pyro = 0xfe925d

class ElementEmote(Enum):
    Anemo = '<:Anemo:1017423315222143066>'
    Cryo = '<:Cryo:1017423337191919666>'
    Dendro = '<:Dendro:1017423353780387841>'
    Electro = '<:Electro:1017423374009503764>'
    Geo = '<:Geo:1017423389624897627>'
    Hydro = '<:Hydro:1017423410357342330>'
    Pyro = '<:Pyro:1017423429638565918>'