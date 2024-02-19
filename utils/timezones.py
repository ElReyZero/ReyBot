from pandas import read_excel
import config as cfg

timezones = read_excel(cfg.PROJECT_PATH + '/utils/data/timezones.xlsx')


def get_iana(tz: str) -> str:
    standard = timezones.loc[timezones["STNDAbbreviation"] == tz]
    if standard.empty:
        return timezones.loc[timezones["DSTAbbreviation"] == "EDT"].iloc[0]["TZ database name"]
    return standard.iloc[0]["TZ database name"]


def get_tz(tz: str) -> str:
    timezone = timezones.loc[timezones['TZ database name'] == str(tz)]
    return timezone.iloc[0]["STNDAbbreviation"]
