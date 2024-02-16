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
    engine = create_engine(DATABASE_URL,
                           pool_pre_ping=True,
                           connect_args={
                               "keepalives": 1,
                               "keepalives_idle": 30,
                               "keepalives_interval": 10,
                               "keepalives_count": 5
                               }
                           )
    GenshinBase.metadata.create_all(engine)
    BotEventsBase.metadata.create_all(engine)