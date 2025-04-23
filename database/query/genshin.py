import logging

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.models.genshin import Constellation, Wish, Weapon, Character
from database.config import Database
from utils.threading import to_thread

log = logging.getLogger('ReyBot')

ART_ICON_PATH = "https://enka.network/ui/UI_Gacha_AvatarImg_"


@to_thread
def push_all_wishes(file: str):
    log.info("SQLAlchemy - Pushing all wishes to database")
    xls = pd.ExcelFile(file)
    with Session(bind=Database.engine) as session:
        for wish_type in ["Character Event", "Weapon Event", "Standard"]:
            df = pd.read_excel(xls, wish_type)
            giga_list = []
            df = df.reset_index()
            for _, row in df.iterrows():
                wish = Wish(type=row['Type'], name=row['Name'], time=row['Time'], stars=row['⭐'], pity=row['Pity'], roll_no=row['#Roll'], group=row['Group'], banner=row['Banner'], wish_type=wish_type)
                giga_list.append(wish)
            try:
                session.add_all(giga_list)
                session.commit()
            except IntegrityError:
                session.rollback()
                print("Batch inserted with some errors. Duplicates found")
                print(f"Count is {session.query(Wish).count()}")


@to_thread
def push_characters(chars: list, task=False):
    log.info("SQLAlchemy - Pushing current characters to database")
    with Session(bind=Database.engine) as session:
        for char in chars:
            if not task:
                log.info(f"SQLAlchemy - Pushing {char.name} to database")
                log.info("SQLAlchemy - Character data:")
                log.info(f"SQLAlchemy - Name: {char.name}")
                log.info(f"SQLAlchemy - Element: {char.element}")
                log.info(f"SQLAlchemy - Level: {char.level}")
                log.info(f"SQLAlchemy - Constellation level: {char.constellation}")
                log.info(f"SQLAlchemy - Friendship level: {char.friendship}")
            char_weapon = session.query(Weapon).filter(Weapon.weapon_id == char.weapon.id).first()
            if not char_weapon:
                char_weapon = Weapon(weapon_id=char.weapon.id, icon=char.weapon.icon, name=char.weapon.name, rarity=char.weapon.rarity,
                                     level=char.weapon.level, type=char.weapon.type, refinement=char.weapon.refinement)
                session.add(char_weapon)
                session.commit()
            constellation_list = []
            try:
                for constellation in char.constellations:
                    constellation_doc = session.query(Constellation).filter(Constellation.constellation_id == constellation.id).first()
                    if not constellation_doc:
                        constellation_doc = Constellation(constellation_id=constellation.id, character_name=char.name, icon=constellation.icon, name=constellation.name, effect=constellation.effect, activated=constellation.activated)
                        session.add(constellation_doc)
                        session.commit()
                    else:
                        constellation_doc.activated = constellation.activated
                        constellation_doc.character_name = char.name
                    constellation_list.append(constellation_doc)
            except AttributeError:
                pass
            char_entry = session.query(Character).filter(Character.character_id == char.id).first()
            if char_entry:
                char_entry.level = char.level
                char_entry.friendship = char.friendship
                char_entry.constellation_level = char.constellation
                char_entry.constellations = constellation_list
                char_entry.weapon = char_weapon
                session.commit()
                if not task:
                    log.info("SQLAlchemy - Character already exists in database. Updating")
                    log.info(f"SQLAlchemy - Updated {char.name} successfully")
            else:
                log.info("SQLAlchemy - Character not found in database, creating new entry")
                char_icon = char.icon.split("/")[-1]
                char_icon = ART_ICON_PATH + char_icon.split(".")[0].split("_")[-1] + ".png"
                char_entry = Character(character_id=char.id, name=char.name, element=char.element, rarity=char.rarity, icon=char_icon, collab=char.collab, level=char.level,
                                       friendship=char.friendship, constellation_level=char.constellation, weapon=char_weapon, constellations=constellation_list)
                session.add(char_entry)
                session.commit()
                log.info(f"SQLAlchemy - Pushed {char.name} successfully as a new entry")
    log.info("SQLAlchemy - Successfully pushed all characters to database")


@to_thread
def get_all_characters() -> list[Character]:
    log.info("SQLAlchemy - Getting all characters from database")
    with Session(bind=Database.engine) as session:
        return session.query(Character).all()


def get_character(name: str, session: Session) -> Character | None:

    log.info(f"SQLAlchemy: Searching for character: {name}")
    char = session.query(Character).filter(Character.name == name).first()
    if not char:
        log.info(f"SQLAlchemy: Character {name} not found")
    return char


def get_weapon_by_obj_id(object_id: str, session: Session) -> Weapon | None:
    with session:
        log.info(f"SQLAlchemy: Searching for weapon with object_id: {object_id}")
        weapon = session.query(Weapon).filter(Weapon.id == object_id).first()
        if not weapon:
            log.info(f"SQLAlchemy: Weapon with object_id {object_id} not found")
        return weapon


@to_thread
def get_character_and_weapon(name: str):
    with Session(bind=Database.engine) as session:
        character = get_character(name, session)
        if character:
            weapon = get_weapon_by_obj_id(character.weapon.id, session)
            return character, weapon
        return None, None
