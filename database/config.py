#pylint: disable=too-few-public-methods, no-member, import-self
import logging
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from database.models.genshin import GenshinBase
from database.models.subscriptions import BotEventsBase
import config as cfg

log = logging.getLogger('ReyBot')

if not cfg.INITIALIZED:
    cfg.get_config()

class Database:

    DATABASE_URL = URL.create(
        "postgresql+psycopg2",
        username=cfg.database["user"],
        password=cfg.database["password"],
        host=cfg.database["host"],
        port=5432,
        database=cfg.database["name"]
    )

    engine = create_engine(DATABASE_URL,
                           pool_pre_ping=True,
                           connect_args={
                               "keepalives": 1,
                               "keepalives_idle": 30,
                               "keepalives_interval": 10,
                               "keepalives_count": 5
                           },
                           )

    GenshinBase.metadata.create_all(engine)
    BotEventsBase.metadata.create_all(engine)


def get_new_session(engine):
    session = sessionmaker(engine)
    return session()
