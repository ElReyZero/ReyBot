import logging
from sqlalchemy import create_engine, URL
from database.models.genshin import GenshinBase
from database.models.subscriptions import BotEventsBase
import config as cfg

log = logging.getLogger('discord')

engine = None

def init_db():
    DATABASE_URL = URL.create(
        "postgresql+psycopg2",
        username=cfg.database["user"],
        password=cfg.database["password"],
        host=cfg.database["host"],
        port=5432,
        database=cfg.database["name"]
    )
    global engine
    engine = create_engine(DATABASE_URL)
    GenshinBase.metadata.create_all(engine)
    BotEventsBase.metadata.create_all(engine)