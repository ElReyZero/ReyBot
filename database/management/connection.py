from mongoengine import connect, disconnect
from config import database
import logging

log = logging.getLogger('discord')

class Connections:
    def __init__(self):
        self.connections = {
            "genshin": {
                "connected": False,
                "connection_name": None
            },
            "pokemon": {
                "connected": False,
                "connection_name": None
            }
        }
        self.used_connections = list()

    def disconnect_all(self):
        for connection in self.connections.keys():
            if self.connections[connection]["connected"]:
                self.disconnect(connection)

    def connect(self, name: str):
        try:
            if not self.connections[name]["connected"]:
                self.connections[name]["connected"] = True
                self.connections[name]["connection_name"] = name
                connect(db=name, host=database['host'], alias=self.connections[name]["connection_name"])
                log.info(f"MongoDB - Connected to database: {name}")
        except KeyError:
            log.critical(f"MongoDB - Attempting to connect - Connection {name} not found.")
            raise Exception(f"Connection {name} not found.")

    def disconnect(self, name: str):
        try:
            if self.connections[name]["connected"]:
                self.connections[name]["connected"] = False
                disconnect(alias=self.connections[name]["connection_name"])
                log.info(f"MongoDB - Disconnected from database: {name}")
        except KeyError:
            log.critical(f"MongoDB - Attempting to disconnect - Connection {name} not found.")
            raise Exception(f"Connection {name} not found.")

def set_connections() -> dict | Connections:
    if database["host"].capitalize() == "None" or database["host"] == "":
        return None
    else:
        return Connections()

def db_exit_handler(connections: dict):
    connections.disconnect_all()
