from pandas import read_excel
try:
    timezones = read_excel('./utils/data/timezones.xlsx')
except FileNotFoundError:
    timezones = read_excel('/home/ReyBot/utils/data/timezones.xlsx')

def getIANA(tz):
    standard = timezones.loc[timezones["STNDAbbreviation"] == tz]
    if standard.empty:
        return timezones.loc[timezones["DSTAbbreviation"] == "EDT"].iloc[0]["TZ database name"]
    else:
        return standard.iloc[0]["TZ database name"]