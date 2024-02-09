from typing import List

from sqlalchemy.orm import Session
from database.models.subscriptions import ServerPanelSubscription
from database.config import engine

def get_all_server_panels() -> List[ServerPanelSubscription]:
    with Session(bind=engine) as session:
        return session.query(ServerPanelSubscription).all()

def get_server_panel_subscription(server: str, channel_id: int) -> ServerPanelSubscription:
    with Session(bind=engine) as session:
        return session.query(ServerPanelSubscription).filter_by(server=server, channel_id=channel_id).first()

def create_server_panel_subscription(server: str, channel_id: int, message_id: int):
    with Session(bind=engine) as session:
        subscription = ServerPanelSubscription(server=server, channel_id=channel_id, message_id=message_id)
        session.add(subscription)
        session.commit()

def delete_server_panel_subscription(server: str, channel_id: int):
    with Session(bind=engine) as session:
        session.query(ServerPanelSubscription).filter_by(server=server, channel_id=channel_id).delete()
        session.commit()
