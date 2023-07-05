from database.models.genshin_firebase import Constellation, Weapon, Character
from utils.threading import to_thread
import logging

log = logging.getLogger('discord')

ART_ICON_PATH = "https://enka.network/ui/UI_Gacha_AvatarImg_"


@to_thread
def push_characters(chars: list, task=False):
    log.info("Firestore - Pushing current characters to database")
    for char in chars:
        if not task:
            log.info(f"Firestore - Pushing {char.name} to database")
            log.info(f"Firestore - Character data:")
            log.info(f"Firestore - Name: {char.name}")
            log.info(f"Firestore - Element: {char.element}")
            log.info(f"Firestore - Level: {char.level}")
            log.info(f"Firestore - Constellation level: {char.constellation}")
            log.info(f"Firestore - Friendship level: {char.friendship}")
        char_weapon = Weapon.collection.filter("weapon_id", "==", char.weapon.id).get()
        if not char_weapon:
            char_weapon = Weapon(weapon_id=char.weapon.id, icon=char.weapon.icon, name=char.weapon.name, rarity=char.weapon.rarity, description=char.weapon.description, level=char.weapon.level, type=char.weapon.type, ascension=char.weapon.ascension, refinement=char.weapon.refinement)
            char_weapon.save()

        constellation_list = list()
        for constellation in char.constellations:
            constellation_doc = Constellation.collection.filter("constellation_id", "==", constellation.id).get()
            if not constellation_doc:
                constellation_doc = Constellation(constellation_id=constellation.id, character_name=char.name, icon=constellation.icon, name=constellation.name, effect=constellation.effect, activated=constellation.activated)
                constellation_doc.save()
            else:
                constellation_doc.activated = constellation.activated
                constellation_doc.character_name = char.name
                constellation_doc.update()
            constellation_list.append(constellation_doc)

        char_doc = Character.collection.filter("character_id", "==", char.id).get()
        if char_doc:
            log.info("Firestore - Character already exists in database. Updating") if not task else ""
            char_doc.level = char.level
            char_doc.friendship = char.friendship
            char_doc.constellation_level = char.constellation
            char_doc.constellations = constellation_list
            char_doc.weapon = char_weapon
            char.update()
            log.info(f"Firestore - Updated {char.name} successfully") if not task else ""
        else:
            log.info("Firestore - Character not found in database, creating new document")
            charIcon = char.icon.split("/")[-1]
            charIcon = ART_ICON_PATH + charIcon.split(".")[0].split("_")[-1] + ".png"
            char = Character(character_id=char.id, name=char.name, element=char.element, rarity=char.rarity, icon=charIcon, collab=char.collab, level=char.level, friendship=char.friendship, constellation_level=char.constellation, weapon=char_weapon, constellations=constellation_list)
            char.save()
            log.info(f"Firestore - Pushed {char.name} successfully as a new Document")
    log.info("Firestore - Successfully pushed all characters to database")

@to_thread
def get_all_characters() -> list[Character]:
    log.info("Firestore - Getting all characters from database")
    return Character.collection.get_all()

@to_thread
def get_character(name: str) -> Character | None:
    log.info(f"Firestore: Searching for character: {name}")
    char = Character.collection.filter("name", "==", name).get()
    if not char:
        log.info(f"Firestore: Character {name} not found")
    return char


@to_thread
def get_weapon_by_obj_id(id: str) -> Weapon | None:
    log.info(f"Firestore: Searching for weapon with object_id: {id}")
    weapon = Weapon.collection.get(id)
    if not weapon:
        log.info(f"Firestore: Weapon with object_id {id} not found")
    return weapon