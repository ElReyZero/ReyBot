from discord.ext.tasks import loop
from database.crud.genshin import push_characters
import config as cfg
import genshin as gi

@loop(hours=24)
async def update_genshin_chars():
    client = gi.Client()
    client.set_cookies(ltuid=cfg.genshin_data["ltuid"], ltoken=cfg.genshin_data["ltoken"])
    chars = await client.get_genshin_characters(cfg.genshin_data["uuid"])
    await push_characters(chars, task=True)
