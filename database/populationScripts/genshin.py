import pandas as pd
from database.classes.genshin import Constellations, Wishes, Weapons, Characters
from pymongo.errors import BulkWriteError
from mongoengine import DoesNotExist
import config as cfg
from datetime import datetime
from utils.threading import to_thread

@to_thread
def push_all_wishes(file):
    if not cfg.connections.connections["genshin"]["connected"]:
        cfg.connections.connect("genshin")
    cfg.connections.connections["genshin"]["last_used"] = datetime.now()
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
def pushCharacters(chars):
    if not cfg.connections.connections["genshin"]["connected"]:
        cfg.connections.connect("genshin")
    cfg.connections.connections["genshin"]["last_used"] = datetime.now()
    for char in chars:
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
            char.update(set__constellations=constellation_list, set__weapon=char_weapon)
        except DoesNotExist:
            char = Characters(character_id=char.id, name=char.name, element=char.element, rarity=char.rarity, icon=char.icon, collab=char.collab, level=char.level, friendship=char.friendship, constellation_level=char.constellation, weapon=char_weapon, constellations=constellation_doc)
            char.save()


def pushGenshin():
    push_all_wishes()
    pushCharacters()