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
