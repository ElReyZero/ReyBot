from discord.ui import View, Button
from discord import ButtonStyle, Interaction
from discord_tools.classes import EventData
from discord_tools.embeds import event_embed
from discord_tools.data import event_dict
import config as cfg

class EventView(View):

    def __init__(self, event_id, owner_id, date, time, timezone, activity, description, player_count, accepted, reserves):
        self.event_id = event_id
        self.owner_id = owner_id
        super().__init__(timeout=None)
        self.add_buttons()
        event_dict[self.event_id] = EventData(self.event_id, self.owner_id, date, time, timezone, activity, description, player_count, accepted, reserves)
        self.event_reference = event_dict[self.event_id]

    def add_buttons(self):
        """_summary_: Adds buttons to the view
        """
        join = Button(label="Unirse", custom_id="join", style=ButtonStyle.green)
        join.callback = self.join
        reserves = Button(label="Reserva", custom_id="reserves", style=ButtonStyle.blurple)
        reserves.callback = self.join_reserves
        edit = Button(label="Editar", custom_id="edit", style=ButtonStyle.blurple)
        edit.callback = self.edit
        borrar = Button(label="Borrar", custom_id="delete", style=ButtonStyle.red)
        borrar.callback = self.delete
        self.add_item(join)
        self.add_item(reserves)
        self.add_item(edit)
        self.add_item(borrar)

    async def join(self, interaction: Interaction):
        if interaction.user.mention in self.event_reference.accepted:
            await interaction.response.send_message(f"{interaction.user.mention} Ya estás inscrito en el evento", ephemeral=True)
            return
        if interaction.user.mention in self.event_reference.reserves:
            self.event_reference.reserves.remove(interaction.user.mention)
        if interaction.user.mention not in self.event_reference.accepted:
            self.event_reference.accepted.append(interaction.user.mention)
        if len(self.event_reference.accepted) + 1 > self.event_reference.player_count:
            await interaction.response.send_message(f"{interaction.user.mention} No puedes unirte a este evento, ya está lleno", ephemeral=True)
            return

        embed = event_embed(self.event_reference.date, self.event_reference.time, self.event_reference.timezone, self.event_reference.activity, self.event_reference.description, self.event_reference.player_count, self.event_reference.accepted, self.event_reference.reserves)
        await interaction.response.edit_message(embed=embed, view=EventView(self.event_reference.event_id, self.event_reference.owner_id, self.event_reference.date, self.event_reference.time, self.event_reference.timezone, self.event_reference.activity, self.event_reference.description, self.event_reference.player_count, self.event_reference.accepted, self.event_reference.reserves))

    async def join_reserves(self, interaction: Interaction):
        if interaction.user.mention in self.event_reference.reserves:
            await interaction.response.send_message(f"{interaction.user.mention} Ya estás en la lista de reservas", ephemeral=True)
            return
        if interaction.user.mention in self.event_reference.accepted:
            self.event_reference.accepted.remove(interaction.user.mention)
        if interaction.user.mention not in self.event_reference.reserves:
            self.event_reference.reserves.append(interaction.user.mention)
        embed = event_embed(self.event_reference.date, self.event_reference.time, self.event_reference.timezone, self.event_reference.activity, self.event_reference.description, self.event_reference.player_count, self.event_reference.accepted, self.event_reference.reserves)
        await interaction.response.edit_message(embed=embed, view=EventView(self.event_reference.event_id, self.event_reference.owner_id, self.event_reference.date, self.event_reference.time, self.event_reference.timezone, self.event_reference.activity, self.event_reference.description, self.event_reference.player_count, self.event_reference.accepted, self.event_reference.reserves))

    async def edit(self, interaction: Interaction):
        if interaction.user.id == self.event_reference.owner_id or interaction.user.id == cfg.MAIN_ADMIN_ID:
            from discord_tools.modals import EventModal
            await interaction.response.send_modal(EventModal(self.event_reference.timezone, event_id=self.event_reference.event_id, is_editing=True, accepted=self.event_reference.accepted))
        else:
            await interaction.response.send_message(f"{interaction.user.mention} No puedes editar este evento ya que no lo creaste", ephemeral=True)

    async def delete(self, interaction: Interaction):
        if interaction.user.id == self.event_reference.owner_id:
            await interaction.response.edit_message(content="Evento borrado", embed=None, view=None)
            if event_dict[self.event_reference.event_id].task:
                event_dict[self.event_reference.event_id].task.cancel()
            del event_dict[self.event_reference.event_id]
        else:
            await interaction.response.send_message("No puedes borrar este evento ya que no lo creaste", ephemeral=True)