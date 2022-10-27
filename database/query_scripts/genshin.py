import pandas as pd
from database.models.genshin import Constellations, Wishes, Weapons, Characters
from pymongo.errors import BulkWriteError
from mongoengine import DoesNotExist
from utils.threading import to_thread
import logging

log = logging.getLogger('discord')

ART_ICON_PATH = "https://enka.network/ui/UI_Gacha_AvatarImg_"

@to_thread
def push_all_wishes(file: str):
    log.info("MongoDB - Pushing all wishes to database")
    xls = pd.ExcelFile(file)
    for wishType in ["Character Event", "Weapon Event", "Standard"]:
        df = pd.read_excel(xls, wishType)
        giga_list = list()
        df = df.reset_index()
        for index, row in df.iterrows():
            wish = Wishes(type=row['Type'], name=row['Name'], time=row['Time'], stars=row['⭐'], pity=row['Pity'], roll_no=row['#Roll'], group=row['Group'], banner=row['Banner'], wish_type=wishType)
            giga_list.append(wish)
        try:
            doc_list = [doc.to_mongo() for doc in giga_list]
            Wishes._get_collection().insert_many(doc_list, ordered=False)
        except BulkWriteError:
            print("Batch inserted with some errors. Duplicates found")
            print(f"Count is {Wishes.objects.count()}")

@to_thread
def push_characters(chars: list, task=False):
    log.info("MongoDB - Pushing current characters to database")
    for char in chars:
        if not task:
            log.info(f"MongoDB - Pushing {char.name} to database")
            log.info(f"MongoDB - Character data:")
            log.info(f"MongoDB - Name: {char.name}")
            log.info(f"MongoDB - Element: {char.element}")
            log.info(f"MongoDB - Level: {char.level}")
            log.info(f"MongoDB - Constellation level: {char.constellation}")
            log.info(f"MongoDB - Friendship level: {char.friendship}")
        try:
            char_weapon = Weapons.objects.get(weapon_id=char.weapon.id)
        except DoesNotExist:
            char_weapon = Weapons(weapon_id=char.weapon.id, icon=char.weapon.icon, name=char.weapon.name, rarity=char.weapon.rarity, description=char.weapon.description, level=char.weapon.level, type=char.weapon.type, ascension=char.weapon.ascension, refinement=char.weapon.refinement)
            char_weapon.save()
        constellation_list = list()
        for constellation in char.constellations:
            try:
                constellation_doc = Constellations.objects.get(constellation_id=constellation.id)
                constellation_doc.update(set__activated=constellation.activated, set__character_name=char.name)
            except DoesNotExist:
                constellation_doc = Constellations(constellation_id=constellation.id, character_name=char.name, icon=constellation.icon, name=constellation.name, effect=constellation.effect, activated=constellation.activated)
                constellation_doc.save()
            constellation_list.append(constellation_doc)
        try:
            filter = {"character_id": char.id}
            newValues = {"$set": {"level":char.level, "friendship":char.friendship, "constellation_level":char.constellation}}
            Characters._get_collection().update_one(filter, newValues)
            char = Characters.objects.get(character_id=char.id)
            log.info("MongoDB - Character already exists in database. Updating") if not task else ""
            char.update(set__constellations=constellation_list, set__weapon=char_weapon)
            log.info(f"MongoDB - Updated {char.name} successfully") if not task else ""
        except DoesNotExist:
            log.info("MongoDB - Character not found in database, creating new document")
            charIcon = char.icon.split("/")[-1]
            charIcon = ART_ICON_PATH + charIcon.split(".")[0].split("_")[-1] + ".png"
            char = Characters(character_id=char.id, name=char.name, element=char.element, rarity=char.rarity, icon=charIcon, collab=char.collab, level=char.level, friendship=char.friendship, constellation_level=char.constellation, weapon=char_weapon, constellations=constellation_list)
            char.save()
            log.info(f"MongoDB - Pushed {char.name} successfully as a new Document")
    log.info("MongoDB - Successfully pushed all characters to database")

@to_thread
def get_all_characters() -> list[Characters]:
    log.info("MongoDB - Getting all characters from database")
    return Characters.objects

@to_thread
def get_character(name: str) -> Characters | None:
    try:
        log.info(f"MongoDB: Searching for character: {name}")
        return Characters.objects.get(name=name)
    except DoesNotExist:
        log.info(f"MongoDB: Character {name} not found")
        return None

@to_thread
def get_weapon_by_obj_id(object_id: str) -> Weapons | None:
    try:
        log.info(f"MongoDB: Searching for weapon with object_id: {object_id}")
        return Weapons.objects.get(id=object_id)
    except DoesNotExist:
        log.info(f"MongoDB: Weapon with object_id {object_id} not found")
        return None