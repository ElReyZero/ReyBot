import asyncio
from json import JSONDecodeError
import backoff
from discord.errors import NotFound
from discord.ext.tasks import loop
import genshin as gi

from database.query.genshin import push_characters
from database.query.subscriptions import get_all_server_panels, delete_server_panel_subscription
from discord_tools.embeds import get_server_panel
from discord_tools.exceptions import RetryException
import config as cfg


@loop(hours=24)
async def update_genshin_chars():
    #return # Disable this task
    client = gi.Client()
    client.set_cookies(cfg.genshin_data)
    chars = await client.get_genshin_characters(cfg.genshin_data["uuid"])
    await push_characters(chars, task=True)


@loop(minutes=5)
async def update_server_panels(bot):

    @backoff.on_exception(backoff.expo, (JSONDecodeError, RetryException), max_tries=5)
    async def update_server_panel(server, channel_id, message_id):
        try:
            channel = bot.get_channel(channel_id)
            message = await channel.fetch_message(message_id)
            embed = get_server_panel(server, is_subscription=True)
            if embed:
                await message.edit(embed=embed)
            else:
                raise RetryException(f"Embed is None for {server.name}")
        except NotFound:
            delete_server_panel_subscription(server, channel_id)
        except AttributeError:
            pass

    messages = get_all_server_panels()

    for message in messages:
        asyncio.create_task(update_server_panel(message.server, message.channel_id, message.message_id))
