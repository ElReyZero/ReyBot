from dataclasses import dataclass, field
import asyncio
from discord import User, Interaction
from datetime import datetime, timedelta
from .data import alert_reminder_dict
from threading import Timer
import sched

@dataclass
class AlertReminder:
    continent: str
    minutes: int
    endTime: datetime
    user: User
    timer: Timer = field(init=False)

    async def send_reminder(self, interaction: Interaction):
        dm = await interaction.user.create_dm()
        await dm.send(f"{interaction.user.mention} Reminder! {self.continent} will end <t:{int(self.endTime.timestamp())}:R>")
        alert_reminder_dict[self.user.id].remove(self)

    def set_scheduler(self, interaction: Interaction, loop: asyncio.AbstractEventLoop):
        loop.create_task(self.send_reminder(interaction))

    def schedule_reminder(self, interaction:Interaction):
        loop = asyncio.get_event_loop()
        localEndTime = datetime.fromtimestamp(self.endTime.timestamp())
        delay = (localEndTime - timedelta(minutes=self.minutes)).timestamp() - datetime.now().timestamp()
        self.scheduler = sched.scheduler()
        self.event = self.scheduler.enter(delay, 1, self.set_scheduler, [interaction, loop])
        loop.run_in_executor(None, self.scheduler.run)

@dataclass
class EventData:
    event_id:str
    owner_id:int
    date:str
    time:str
    timezone:str
    activity:str
    description:str
    player_count:int
    accepted:list = field(default_factory=list)
    reserves:list = field(default_factory=list)
    task:asyncio.Task = field(default=None)
    message_id:int = field(default=None)

    def to_json(self):
        return {
            "event_id": self.event_id,
            "owner_id": self.owner_id,
            "date": self.date,
            "time": self.time,
            "timezone": self.timezone,
            "activity": self.activity,
            "description": self.description,
            "player_count": self.player_count,
            "accepted": self.accepted,
            "reserves": self.reserves
        }