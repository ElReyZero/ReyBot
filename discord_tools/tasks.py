from discord.ext.tasks import loop
from database.query_scripts.genshin import push_characters
from database.query_scripts.genshin_firebase import push_characters as push_characters_fb
import config as cfg
import genshin as gi

@loop(hours=24)
async def update_genshin_chars():
    client = gi.Client()
    client.set_cookies(ltuid=cfg.genshin_data["ltuid"], ltoken=cfg.genshin_data["ltoken"])
    chars = await client.get_genshin_characters(cfg.genshin_data["uuid"])
    await push_characters(chars, task=True)
    await push_characters_fb(chars, task=True)
