import pandas as pd
# Alert Reminder Stuff
alert_reminder_dict = {}

timezones = pd.read_excel('./discord_tools/data/timezones.xlsx')

def getIANATz(tz):
    standard = timezones.loc[timezones["STNDAbbreviation"] == tz]
    if standard.empty:
        return timezones.loc[timezones["DSTAbbreviation"] == "EDT"].iloc[0]["TZ database name"]
    else:
        return standard.iloc[0]["TZ database name"]