from discord.ext.tasks import loop
from database.query_scripts.genshin import pushCharacters
import config as cfg
import genshin as gi

@loop(hours=24)
async def updateGenshinChars():
    client = gi.Client()
    client.set_cookies(ltuid=cfg.genshin_data["ltuid"], ltoken=cfg.genshin_data["ltoken"])
    chars = await client.get_genshin_characters(cfg.genshin_data["uuid"])
    await pushCharacters(chars, task=True)
