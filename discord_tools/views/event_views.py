from discord.ui import View, Button
from discord import ButtonStyle, Interaction
from discord_tools.embeds import event_embed
from discord_tools.data import event_dict


class EventView(View):

    def __init__(self, event_id, owner_id, date, time, timezone, activity, description, player_count, accepted, reserves):
        self.event_id = event_id
        self.owner_id = owner_id
        self.date = date
        self.time = time
        self.timezone = timezone
        self.activity = activity
        self.description = description
        self.accepted = accepted if len(accepted) > 0 else [f"<@{owner_id}>"]
        self.reserves = reserves
        self.player_count = player_count
        super().__init__(timeout=None)
        self.add_buttons()
        event_dict[self.event_id] = self

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
        if interaction.user.mention in self.reserves:
            self.reserves.remove(interaction.user.mention)
        if interaction.user.mention not in self.accepted:
            self.accepted.append(interaction.user.mention)
        if len(self.accepted) + 1 > self.player_count:
            await interaction.response.send_message("No puedes unirte a este evento, ya está lleno", ephemeral=True)
            return

        embed = event_embed(self.date, self.time, self.timezone, self.activity, self.description, self.player_count, self.accepted, self.reserves)
        await interaction.response.edit_message(embed=embed, view=EventView(self.event_id, self.owner_id, self.date, self.time, self.timezone, self.activity, self.description, self.player_count, self.accepted, self.reserves))

    async def join_reserves(self, interaction: Interaction):
        if interaction.user.mention in self.accepted:
            self.accepted.remove(interaction.user.mention)
        if interaction.user.mention not in self.reserves:
            self.reserves.append(interaction.user.mention)
        embed = event_embed(self.date, self.time, self.timezone, self.activity, self.description, self.player_count, self.accepted, self.reserves)
        await interaction.response.edit_message(embed=embed, view=EventView(self.event_id, self.owner_id, self.date, self.time, self.timezone, self.activity, self.description, self.player_count, self.accepted, self.reserves))

    async def edit(self, interaction: Interaction):
        if interaction.user.id == self.owner_id:
            from discord_tools.modals import EventModal
            await interaction.response.send_modal(EventModal(self.timezone, event_id=self.event_id, is_editing=True, accepted=self.accepted))
        else:
            await interaction.response.send_message("No puedes editar este evento ya que no lo creaste", ephemeral=True)

    async def delete(self, interaction: Interaction):
        if interaction.user.id == self.owner_id:
            await interaction.response.edit_message(content="Evento borrado", embed=None, view=None)
            del event_dict[self.event_id]
        else:
            await interaction.response.send_message("No puedes borrar este evento ya que no lo creaste", ephemeral=True)