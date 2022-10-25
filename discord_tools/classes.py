from dataclasses import dataclass, field
import asyncio
from discord import User
from datetime import datetime, timedelta
from .data import alert_reminder_dict

@dataclass
class AlertReminder:
    continent:str
    minutes:int
    endTime: datetime
    user:User
    task:asyncio.Task = field(init=False)

    async def check_remaining_reminder_time(self, interaction):
        while True:
            await asyncio.sleep(1)
            current_time = datetime.now().replace(microsecond=0)
            localEndTime = datetime.fromtimestamp(self.endTime.timestamp())
            reminder = localEndTime - timedelta(minutes=self.minutes)
            if current_time == reminder or current_time > reminder:
                dm = await interaction.user.create_dm()
                await dm.send(f"{interaction.user.mention} Reminder! {self.continent} will end <t:{int(self.endTime.timestamp())}:R>")
                alert_reminder_dict[self.user.id].remove(self)
                break

    def set_task(self, task):
        self.task = task