#pylint: disable=too-few-public-methods
import uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.schema import MetaData

class BotEventsBase(DeclarativeBase):
    metadata = MetaData(schema='bot_events')

class ServerPanelSubscription(BotEventsBase):
    __tablename__ = 'server_panel_subscriptions'

    id : Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    server : Mapped[str] = mapped_column(nullable = False)
    channel_id : Mapped[int] =  mapped_column(nullable=False)
    message_id : Mapped[int] = mapped_column(nullable=False)
