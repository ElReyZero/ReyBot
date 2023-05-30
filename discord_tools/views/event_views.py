from discord.ui import View, Button
from discord import ButtonStyle, Interaction
from discord_tools.embeds import event_embed
from discord_tools.data import event_dict
import config as cfg

class EventView(View):

    def __init__(self, event_id, owner_id):
        self.event_id = event_id
        self.owner_id = owner_id
        super().__init__(timeout=None)
        self.add_buttons()

    def add_buttons(self):
        """_summary_: Adds buttons to the view
        """
        join = Button(label="Unirse", custom_id="join", style=ButtonStyle.green)
        join.callback = self.join
        reserves = Button(label="Reserva", custom_id="reserves", style=ButtonStyle.blurple)
        reserves.callback = self.join_reserves
        leave = Button(label="Salir", custom_id="leave", style=ButtonStyle.red)
        leave.callback = self.leave
        edit = Button(label="Editar", custom_id="edit", style=ButtonStyle.blurple)
        edit.callback = self.edit
        delete = Button(label="Borrar", custom_id="delete", style=ButtonStyle.red)
        delete.callback = self.delete_event
        self.add_item(join)
        self.add_item(reserves)
        self.add_item(leave)
        self.add_item(edit)
        self.add_item(delete)

    async def join(self, interaction: Interaction):
        if interaction.user.mention in event_dict[self.event_id].accepted:
            await interaction.response.send_message(f"{interaction.user.mention} Ya estás inscrito en el evento", ephemeral=True)
            return
        if len(event_dict[self.event_id].accepted) + 1 > event_dict[self.event_id].player_count:
            await interaction.response.send_message(f"{interaction.user.mention} No puedes unirte a este evento, ya está lleno", ephemeral=True)
            return
        if interaction.user.mention in event_dict[self.event_id].reserves:
            event_dict[self.event_id].reserves.remove(interaction.user.mention)
        if interaction.user.mention not in event_dict[self.event_id].accepted:
            event_dict[self.event_id].accepted.append(interaction.user.mention)

        embed = event_embed(self.event_id, event_dict[self.event_id].date, event_dict[self.event_id].time, event_dict[self.event_id].timezone, event_dict[self.event_id].activity, event_dict[self.event_id].description, event_dict[self.event_id].player_count, event_dict[self.event_id].accepted, event_dict[self.event_id].reserves)
        await interaction.response.edit_message(embed=embed)

    async def join_reserves(self, interaction: Interaction):
        if interaction.user.mention in event_dict[self.event_id].reserves:
            await interaction.response.send_message(f"{interaction.user.mention} Ya estás en la lista de reservas", ephemeral=True)
            return
        if interaction.user.mention in event_dict[self.event_id].accepted:
            event_dict[self.event_id].accepted.remove(interaction.user.mention)
        if interaction.user.mention not in event_dict[self.event_id].reserves:
            event_dict[self.event_id].reserves.append(interaction.user.mention)
        embed = event_embed(self.event_id, event_dict[self.event_id].date, event_dict[self.event_id].time, event_dict[self.event_id].timezone, event_dict[self.event_id].activity, event_dict[self.event_id].description, event_dict[self.event_id].player_count, event_dict[self.event_id].accepted, event_dict[self.event_id].reserves)
        await interaction.response.edit_message(embed=embed)

    async def leave(self, interaction: Interaction):
        if interaction.user.mention not in event_dict[self.event_id].accepted and interaction.user.mention not in event_dict[self.event_id].reserves:
            await interaction.response.send_message(f"{interaction.user.mention} No estás inscrito en el evento", ephemeral=True)
            return
        if interaction.user.mention in event_dict[self.event_id].accepted:
            event_dict[self.event_id].accepted.remove(interaction.user.mention)
        if interaction.user.mention in event_dict[self.event_id].reserves:
            event_dict[self.event_id].reserves.remove(interaction.user.mention)
        embed = event_embed(self.event_id, event_dict[self.event_id].date, event_dict[self.event_id].time, event_dict[self.event_id].timezone, event_dict[self.event_id].activity, event_dict[self.event_id].description, event_dict[self.event_id].player_count, event_dict[self.event_id].accepted, event_dict[self.event_id].reserves)
        await interaction.response.edit_message(embed=embed)

    async def edit(self, interaction: Interaction):
        if interaction.user.id == event_dict[self.event_id].owner_id or interaction.user.id == cfg.MAIN_ADMIN_ID:
            from discord_tools.modals import EventModal
            await interaction.response.send_modal(EventModal(event_dict[self.event_id].timezone, event_id=self.event_id, is_editing=True, accepted=event_dict[self.event_id].accepted))
        else:
            await interaction.response.send_message(f"{interaction.user.mention} No puedes editar este evento ya que no lo creaste", ephemeral=True)

    async def delete_event(self, interaction: Interaction):
        if interaction.user.id == event_dict[self.event_id].owner_id:
            await interaction.response.edit_message(content="Evento borrado", embed=None, view=None)
            try:
                if event_dict[self.event_id].event:
                    event_dict[self.event_id].scheduler.cancel(event_dict[self.event_id].event)
            except AttributeError:
                pass
            del event_dict[self.event_id]
        else:
            await interaction.response.send_message("No puedes borrar este evento ya que no lo creaste", ephemeral=True)