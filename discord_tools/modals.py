from discord.ui import Modal, TextInput
from discord_tools.classes import EventData
from discord_tools.embeds import event_embed
from discord import TextStyle, Interaction
from discord_tools.views.event_views import EventView
import asyncio
from datetime import datetime
from pytz import timezone as pytz_tz
from utils.timezones import get_IANA
import config as cfg
from discord_tools.data import event_dict
import uuid
import sched

class EventModal(Modal, title="Crear Evento"):

    activity = TextInput(label="Actividad", placeholder="Selecciona una actividad",
                         style=TextStyle.short, required=True, max_length=100)
    description = TextInput(label="Descripción", placeholder="Describe la actividad o sus requerimientos",
                            style=TextStyle.paragraph, required=True, max_length=250)
    date = TextInput(label="Fecha", placeholder="Fecha con formato (DD/MM/AAAA)",
                     style=TextStyle.short, required=True, min_length=10, max_length=10)
    time = TextInput(label="Hora", placeholder="Hora en formato de 24 horas (HH:MM)",
                     style=TextStyle.short, required=True, min_length=5, max_length=5)
    player_count = TextInput(label="Número de jugadores", placeholder="Escribe un número entre 2 y 12",
                             style=TextStyle.short, required=True, min_length=1, max_length=2)

    def __init__(self, timezone, event_id=None, is_editing=False, accepted=list(), reserves=list()):
        self.event_id = str(uuid.uuid4()) if not event_id else event_id
        self.timezone = timezone
        self.is_editing = is_editing
        self.accepted = accepted
        self.reserves = reserves
        super().__init__()

        if is_editing:
            self.activity.default = event_dict[event_id].activity
            self.description.default = event_dict[event_id].description
            self.date.default = event_dict[event_id].date
            self.time.default = event_dict[event_id].time
            self.player_count.default = str(event_dict[event_id].player_count)

    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer()
        try:
            player_count = int(self.player_count.value)
            if player_count < 2 or player_count > 12:
                await interaction.followup.send(f"{interaction.user.mention} El número de jugadores debe de estar entre 2 y 12", ephemeral=True)
                return
        except ValueError:
            await interaction.followup.send(f"{interaction.user.mention} El número de jugadores debe de ser un número", ephemeral=True)
            return
        time = self.time.value.split(":")
        date = datetime.strptime(self.date.value, "%d/%m/%Y")
        timestamp = date.replace(hour=int(time[0]), minute=int(time[1]))
        timezone_py = pytz_tz(get_IANA(self.timezone))
        event_time = timezone_py.localize(
            timestamp).astimezone(None).timestamp()
        if event_time < datetime.now().timestamp():
            await interaction.followup.send(f"{interaction.user.mention} No puedes crear eventos en el pasado. La fecha y hora debe ser posterior a <t:{int(datetime.now().timestamp())}>", ephemeral=True)
            return
        try:
            if not event_dict.get(self.event_id):
                event_dict[self.event_id] = EventData(self.event_id, interaction.user.id, self.date.value, self.time.value, self.timezone, self.activity.value, self.description.value, int(
                    self.player_count.value), self.accepted if self.is_editing else [interaction.user.mention], self.reserves if self.is_editing else list())
            embed = event_embed(self.event_id, self.date.value, self.time.value, self.timezone,
                                self.activity.value, self.description.value, self.player_count.value, accepted=self.accepted if self.is_editing else [interaction.user.mention], reserves=self.reserves if self.is_editing else list())

            if self.is_editing:
                event_dict[self.event_id].task.cancel()
                event_dict[self.event_id].activity = self.activity.value
                event_dict[self.event_id].description = self.description.value
                event_dict[self.event_id].date = self.date.value
                event_dict[self.event_id].time = self.time.value
                event_dict[self.event_id].player_count = int(
                    self.player_count.value)
                view = EventView(event_id=self.event_id,
                                 owner_id=interaction.user.id)
                await interaction.followup.edit(embed=embed, view=view)
            else:
                message = await interaction.followup.send(embed=embed, view=EventView(event_id=self.event_id, owner_id=interaction.user.id))
                event_dict[self.event_id].message_id = message.id

            self.schedule_event_time(interaction, self.event_id, self.activity.value, self.date.value, self.time.value, self.timezone)
        except AttributeError:
            await interaction.followup.send(f"{interaction.user.mention} Formato de fecha inválido", ephemeral=True)
            raise
        except (IndexError, ValueError):
            await interaction.followup.send(f"{interaction.user.mention} Formato de hora inválido, el formato debe de estar en HH:MM (24h)", ephemeral=True)

    async def send_reminder(self, interaction: Interaction, event_id, activity):
        try:
            event_dict[event_id]
        except KeyError:
            return
        user_list_str = ""
        for user in event_dict[event_id].accepted:
            user_list_str += f"{user} "
        await interaction.followup.send(f"{user_list_str}El evento '{activity}' ha empezado")
        await asyncio.sleep(600)
        await interaction.channel.purge(limit=5, check=lambda m: m.author.id == cfg.bot_id)
        del event_dict[event_id]

    def set_scheduler(self, interaction: Interaction, event_id:str, activity:str, loop: asyncio.AbstractEventLoop):
        loop.create_task(self.send_reminder(interaction, event_id, activity))

    def schedule_event_time(self, interaction: Interaction, event_id, activity, date, time, timezone):
        time = time.split(":")
        date = datetime.strptime(date, "%d/%m/%Y")
        timestamp = date.replace(hour=int(time[0]), minute=int(time[1]))
        timezone_py = pytz_tz(get_IANA(timezone))
        event_time = timezone_py.localize(timestamp).astimezone(None).timestamp()
        loop = asyncio.get_event_loop()
        delay = event_time - datetime.now().timestamp()
        self.scheduler = sched.scheduler()
        self.event = self.scheduler.enter(delay, 1, self.set_scheduler, [interaction, event_id, activity, loop])
        loop.run_in_executor(None, self.scheduler.run)