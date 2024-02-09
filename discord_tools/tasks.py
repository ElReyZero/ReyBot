from json import JSONDecodeError
from discord.errors import NotFound
from discord.ext.tasks import loop
from database.query.genshin import push_characters
from database.query.subscriptions import get_all_server_panels, delete_server_panel_subscription

from discord_tools.embeds import get_server_panel

import config as cfg
import genshin as gi

@loop(hours=24)
async def update_genshin_chars():
    client = gi.Client()
    client.set_cookies(ltuid=cfg.genshin_data["ltuid"], ltoken=cfg.genshin_data["ltoken"])
    chars = await client.get_genshin_characters(cfg.genshin_data["uuid"])
    await push_characters(chars, task=True)


@loop(minutes=5)
async def update_server_panels(bot):

    async def update_server_panel(server, channel_id, message_id):
        try:
            channel = bot.get_channel(channel_id)
            message = await channel.fetch_message(message_id)
            embed = get_server_panel(server, is_subscription=True)
            await message.edit(embed=embed)
        except NotFound:
            delete_server_panel_subscription(server, channel_id)
        except JSONDecodeError:
            pass

    messages = get_all_server_panels()

    for message in messages:
        await update_server_panel(message.server, message.channel_id, message.message_id)
