from pandas import read_excel
import config as cfg

timezones = read_excel(cfg.PROJECT_PATH + '/utils/data/timezones.xlsx')

def getIANA(tz):
    standard = timezones.loc[timezones["STNDAbbreviation"] == tz]
    if standard.empty:
        return timezones.loc[timezones["DSTAbbreviation"] == "EDT"].iloc[0]["TZ database name"]
    else:
        return standard.iloc[0]["TZ database name"]

def getTZ(tz):
    timezone = timezones.loc[timezones['TZ database name'] == str(tz)]
    return timezone.iloc[0]["STNDAbbreviation"]