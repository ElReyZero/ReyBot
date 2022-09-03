import pandas as pd
# Alert Reminder Stuff
alert_reminder_dict = {}

try:
    timezones = pd.read_excel('./discord_tools/data/timezones.xlsx')
except FileNotFoundError:
    timezones = pd.read_csv('/home/ReyBot/discord_tools/timezones.xlsx')

def getIANATz(tz):
    standard = timezones.loc[timezones["STNDAbbreviation"] == tz]
    if standard.empty:
        return timezones.loc[timezones["DSTAbbreviation"] == "EDT"].iloc[0]["TZ database name"]
    else:
        return standard.iloc[0]["TZ database name"]