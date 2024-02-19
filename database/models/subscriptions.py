#pylint: disable=too-few-public-methods
import uuid
from sqlalchemy import Column, String, BigInteger
from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import MetaData
from sqlalchemy.dialects.postgresql import UUID

BotEventsBase = declarative_base(metadata=MetaData(schema='bot_events'))

class ServerPanelSubscription(BotEventsBase):
    __tablename__ = 'server_panel_subscriptions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    server = Column(String, nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)
