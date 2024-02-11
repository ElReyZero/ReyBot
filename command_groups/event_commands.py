from typing import Literal
from json import JSONDecodeError
from discord import app_commands, Interaction, ButtonStyle
from discord.ui import Button, View
from discord.errors import NotFound
from discord.ext import commands
from discord_tools.embeds import get_server_panel
from database.query.subscriptions import get_server_panel_subscription, create_server_panel_subscription, delete_server_panel_subscription

@app_commands.guild_only()
class SubscribeToEvents(commands.GroupCog, name="server_panel", description="Subscribe this channel to bot events"):

    @app_commands.command(name="subscribe", description="Subscribe this channel to the PS2 server panel embed")
    async def subscribe_to_server_panel(self, interaction : Interaction, server: Literal["Emerald", "Connery", "Cobalt", "Miller", "Soltech", "Jaeger", "Genudine", "Ceres"] = "Emerald"):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(f"{interaction.user.mention} You don't have the required permissions to use this command", ephemeral=True)
            return
        await interaction.response.defer()

        channel_id = interaction.channel_id
        current_message = get_server_panel_subscription(server, channel_id)
        if current_message:
            await interaction.followup.send(f"{interaction.user.mention} This channel is already subscribed to server panel for {server}", ephemeral=True)
            return
        try:
            embed = get_server_panel(server, is_subscription=True)
        except JSONDecodeError:
            await interaction.followup.send("Can't fetch data from Honu (It's most likely down). Please try again later.")
            return
        await interaction.followup.send(f"{interaction.user.mention} Subscribed this channel to server panel for {server}", ephemeral=True)
        message = await interaction.channel.send(embed=embed)
        create_server_panel_subscription(server, channel_id, message.id)

    @app_commands.command(name="unsubscribe", description="Unsubscribe this channel from the PS2 server panel embed")
    async def unsubscribe_from_server_panel(self, interaction : Interaction, server: Literal["Emerald", "Connery", "Cobalt", "Miller", "Soltech", "Jaeger", "Genudine", "Ceres"] = "Emerald"):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(f"{interaction.user.mention} You don't have the required permissions to use this command", ephemeral=True)
            return

        channel_id = interaction.channel_id
        current_message = get_server_panel_subscription(server, channel_id)
        if current_message:
            try:
                discord_message = await interaction.channel.fetch_message(current_message.message_id)
                await discord_message.delete()
            except NotFound:
                pass
            await interaction.response.send_message(f"{interaction.user.mention} Unsubscribed this channel from server panel for {server}", ephemeral=True)
            delete_server_panel_subscription(server, channel_id)
        else:
            await interaction.response.send_message(f"{interaction.user.mention} This channel is not subscribed to server panel for {server}", ephemeral=True)

    @app_commands.command(name="get", description="Check the active alerts and open continents on a server. Default: Emerald")
    async def check_server_panel(self, interaction: Interaction, server: Literal["Emerald", "Connery", "Cobalt", "Miller", "Soltech", "Jaeger", "Genudine", "Ceres"] = "Emerald"):
        try:
            embed = get_server_panel(server)
            if embed:
                refresh = Button(
                    label="Refresh", custom_id="refresh_alerts", style=ButtonStyle.blurple)

                async def refresh_callback(interaction):
                    await interaction.response.defer()
                    try:
                        embed = get_server_panel(server)
                        await interaction.edit_original_response(embed=embed)
                    except NotFound:
                        pass
                    except JSONDecodeError:
                        await interaction.followup.send("Can't fetch data from Honu (It's most likely down). Please try again later.")
                        return
                refresh.callback = refresh_callback
                view = View(timeout=None)
                view.add_item(refresh)
                await interaction.response.send_message(embed=embed, view=view)
            else:
                await interaction.response.send_message(f"Can't fetch data from Honu or ps2alerts.com (It's most likely down). Please try again later.")
        except JSONDecodeError:
            await interaction.followup.send("Can't fetch data from Honu (It's most likely down). Please try again later.")
            return